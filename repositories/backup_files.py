from datetime import timezone
from typing import List
import os

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from common.schemas import FileInfo
from db.models import BackupFileOrm, BucketOrm
from services.utils import log_vars


def create_backup_file(session: Session, backup_file: BackupFileOrm) -> BackupFileOrm:
    session.add(backup_file)
    return backup_file


def update_backup_file(session: Session, backup_file_id: int, update_data: dict) -> BackupFileOrm | None:
    backup_file = session.scalar(select(BackupFileOrm).where(BackupFileOrm.id == backup_file_id))
    if not backup_file:
        return None
    for key, value in update_data.items():
        setattr(backup_file, key, value)
    session.commit()
    return backup_file


def get_backup_file_by_id(session: Session, backup_file_id: int) -> BackupFileOrm | None:
    return session.query(BackupFileOrm).filter(BackupFileOrm.id == backup_file_id).one_or_none()


def get_backup_file_by_path_and_name(session: Session, bucket_id: int, path: str, name: str) -> BackupFileOrm | None:
    return session.query(BackupFileOrm).filter(
        and_(
            BackupFileOrm.bucket_id == bucket_id,
            BackupFileOrm.path == path,
            BackupFileOrm.name == name,
        )
    ).one_or_none()


def get_backup_file_by_details(
    session: Session,
    storage_id: int,
    bucket_id: int,
    path: str,
    file_name: str
) -> BackupFileOrm | None:
    """
    Возвращает экземпляр BackupFileOrm по указанным параметрам.
    """
    backup_file = session.query(BackupFileOrm).filter_by(
        storage_id=storage_id,
        bucket_id=bucket_id,
        path=path,
        file_name=file_name
    ).one_or_none()
    return backup_file


def list_backed_up_files(session: Session, storage_id: int, bucket_id: int) -> List[FileInfo]:
    """
    :param session:
    :param storage_id:
    :param bucket_id:
    :return:
    """
    result = session.query(
        BackupFileOrm.file_name,
        BackupFileOrm.file_size,
        BackupFileOrm.file_time,
        BackupFileOrm.path,
        BucketOrm.path.label('bucket_path')
    ).join(
        BucketOrm, BackupFileOrm.bucket_id == BucketOrm.id
    ).filter(
        BackupFileOrm.storage_id == storage_id,
        BackupFileOrm.bucket_id == bucket_id
    ).all()

    def _build_file_path(file: BackupFileOrm) -> str:
        return str(os.path.join(file.bucket_path, file.path, file.file_name))

    log_vars('list_backed_up_files.log', result=result)

    return [
        FileInfo(
            path=_build_file_path(file),
            size=file.file_size,
            time=file.file_time.replace(tzinfo=timezone.utc) if file.file_time.tzinfo is None else file.file_time
        )
        for file in result
    ]
