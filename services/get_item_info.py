from pathlib import Path
from typing import Dict, List

from sqlalchemy.orm import Session

from common.BackupConfig import BackupConfig
from common.schemas import BackupDTO, BucketAddDTO, BucketDTO, S3BackupFileDTO, FileInfo, BackupItem
from db.models import BucketOrm, BackupFileOrm
from repositories.backup_files import list_backed_up_files
from services.bucket_orm import get_bucket_by_storage_and_path
from services.s3_storages_orm import get_storage_by_name_service
from datetime import datetime


async def get_bucket_config_by_name(item_name: str) -> BackupItem:
    config = BackupConfig()
    settings = config.get_settings()

    # Извлечение нужного словаря из списка 's3_storages'
    s3_storages = settings.get('s3_storages', [])

    # Находим словарь с нужным bucket_name
    item_dict = None
    for storage in s3_storages:
        items = storage.get('items', [])
        item_dict = next((item for item in items if item.get('name') == item_name), None)
        if item_dict:
            break

    if item_dict:
        # Создание объекта BackupItem
        backup_item = BackupItem(**item_dict)
    else:
        # Обработка случая, когда item_dict не найден
        raise ValueError(f"No backup item found with bucket name {item_name}")
    return backup_item


async def get_bucket_info_service(data: BackupDTO) -> Dict[str, List[FileInfo]]:
    # Находим storage и bucket в конфиге (json)
    bucket: BackupItem = await get_bucket_config_by_name(data.item)

    # Собираем список реальных файлов
    real_files: List[FileInfo] = list_files_recursive(bucket.path, bucket.include, bucket.exclude)

    # Ищем storage в БД
    s3_storage = get_storage_by_name_service(data.storage)
    if s3_storage is None:
        backed_up_files = []
        # return {'message': 'No backups found for storage %s' % data.storage}
    else:
        bucket = await get_bucket_by_storage_and_path(s3_storage.id, bucket.path)
        with Session() as session:
            # Собираем список файлов из БД
            backed_up_files: List[FileInfo] = await list_backed_up_files(
                session=session,
                storage_id=s3_storage.id,
                bucket_id=bucket.id
            )
    # Сравниваем списки
    new_files = [file for file in real_files if file not in backed_up_files]
    updated_files = [file for file in real_files if file in backed_up_files and file.time != backed_up_files[backed_up_files.index(file)].time]
    deleted_files = [file for file in backed_up_files if file not in real_files]
    return {'status': 'Ok', 'new': new_files, 'updated': updated_files, 'deleted': deleted_files}


def list_files_recursive(
    directory_path: str,
    include_extensions: List[str] = None,
    exclude_extensions: List[str] = None,
    include_subdirectories: bool = True
) -> List[FileInfo]:
    def _is_extension_allowed(
        entry: Path,
        include_extensions: List[str] = None,
        exclude_extensions: List[str] = None
    ) -> bool:
        if include_extensions and exclude_extensions:
            raise ValueError("Cannot specify both include_extensions and exclude_extensions at the same time.")

        if include_extensions and not include_extensions:
            return False  # Просто проверяем, что list isn't empty

        if include_extensions:  # Если есть include Extensions, исключаем исключения
            return entry.suffix.lower().replace('.', '') in include_extensions

        if exclude_extensions:  # Если include Extensions None, то исключаем список exclude Extensions
            return entry.suffix.lower().replace('.', '') not in exclude_extensions

        # Если ни include, ни exclude не указанные, вернется True для любых файлов
        return True

    def _get_file_info(file_path: Path) -> FileInfo:
        try:
            size = file_path.stat().st_size
            time = datetime.fromtimestamp(file_path.stat().st_mtime)
        except FileNotFoundError:
            size, time = None, None
        return FileInfo(path=file_path.as_posix(), size=size, time=time)

    def _list_dir(directory: Path, depth: int = 0) -> List[FileInfo]:
        info_list = []
        for entry in directory.iterdir():
            if entry.is_file():
                if _is_extension_allowed(entry, include_extensions, exclude_extensions):
                    info_list.append(_get_file_info(entry))
            else:
                info_list.extend(_list_dir(entry, depth + 1))
        return info_list

    file_dir = Path(directory_path)
    return _list_dir(file_dir)
