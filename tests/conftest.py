import os
import random
from datetime import datetime, timezone
from fileinput import filename
from typing import List

import pytest
from alembic import command
from alembic.config import Config

from common.BackupConfig import BackupConfig
from common.settings import ROOT_DIR, settings
from db.engine import Session
from db.models import S3StorageOrm, BackupFileOrm
from repositories.backup_files import create_backup_file
from repositories.s3_storages import create_storage
from schemas import S3StorageDTO, S3BackupFileDTO, S3BackupFileRelDTO, S3StorageRelDTO, BackupItem
import os
import time


TEST_BACKUP_DIR = os.path.join(ROOT_DIR, 'tests', 'files_for_tests')

@pytest.fixture
def apply_migrations():
    db_path = settings.TEST_DB_DSN.replace('sqlite:///', '')
    assert 'test' in os.path.basename(db_path).lower(), 'Попытка использовать не тестовую SQLite базу данных.'

    alembic_cfg = Config(str(ROOT_DIR / 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', str(ROOT_DIR / 'alembic'))
    command.downgrade(alembic_cfg, 'base')
    command.upgrade(alembic_cfg, 'head')

    yield command, alembic_cfg

    # command.downgrade(alembic_cfg, 'base')
    # if os.path.exists(db_path):
    #     os.remove(db_path)


@pytest.fixture
def s3_storage_model(faker) -> S3StorageOrm:
    return S3StorageOrm(
        name=faker.name(),
        url=f"test://{faker.bothify('???????.??/???????/?????????###')}",
        access_key=faker.address(),
        secret_key=faker.bothify('?#?#?#?#?#?#?#?#'),
    )


@pytest.fixture
def s3_backup_file_model(s3_storage_model, faker) -> BackupFileOrm:
    return BackupFileOrm(
        storage=s3_storage_model,
        path=faker.name,
        file_name=faker.address,
        file_size=random.randint(0, 1000),
        file_time=faker.date_between(start_date='-12m', end_date='today'),
        created_at=faker.date_between(start_date='-12m', end_date='today'),
    )


@pytest.fixture
def s3_storage_schema(s3_storage_model, faker) -> S3StorageDTO:
    return S3StorageDTO.model_validate(s3_storage_model, from_attributes=True)


@pytest.fixture
def created_s3_storage_dto(s3_storage_model) -> S3StorageRelDTO:
    with Session() as session:
        create_storage(session, s3_storage_model)
        session.commit()
        # return s3_storage_model
        return S3StorageRelDTO.model_validate(s3_storage_model, from_attributes=True)


@pytest.fixture
def created_s3_storage_orm(s3_storage_model) -> S3StorageOrm:
    with Session() as session:
        create_storage(session, s3_storage_model)
        session.commit()
        return s3_storage_model


# === Backup file
@pytest.fixture
def s3_backup_file_schema():
    backup_files = os.listdir(TEST_BACKUP_DIR)
    backup_file_name = random.choice(backup_files)
    backup_file_name_with_path = os.path.join(TEST_BACKUP_DIR, backup_file_name)
    file_size = os.path.getsize(backup_file_name_with_path)
    file_time = os.path.getmtime(backup_file_name_with_path)
    return S3BackupFileDTO(
        path=TEST_BACKUP_DIR,
        file_name=backup_file_name,
        file_size=file_size,
        file_time=file_time,
        created_at=None,
    )


@pytest.fixture
def created_backup_file(s3_backup_file_model):
    with Session() as session:
        create_storage(session, s3_backup_file_model.storage)
        create_backup_file(session, s3_backup_file_model)


def get_backup_files_info(
    path: str,
    include: list,
    exclude: list,
) -> List[S3BackupFileDTO]:
    if include is None:
        include = []
    if exclude is None:
        exclude = []

    if include and exclude:
        raise ValueError("Cannot specify both 'include' and 'exclude' lists.")

    file_info_list = []

    # Проверка, является ли путь директорией
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()

                # Проверка расширений файла
                if include and file_extension not in include:
                    continue
                if exclude and file_extension in exclude:
                    continue

                file_path = os.path.join(root, file)
                file_info = S3BackupFileDTO(
                    path=os.path.relpath(root, path),
                    file_name=file,
                    file_size=os.path.getsize(file_path),
                    file_time=time.ctime(os.path.getmtime(file_path))
                )
                file_info_list.append(file_info)

    # Проверка, является ли путь файлом
    elif os.path.isfile(path):
        file_extension = os.path.splitext(path)[1].lower()

        # Проверка расширений файла
        if include and file_extension not in include:
            return []
        if exclude and file_extension in exclude:
            return []
        file_path, file_name = os.path.split(path)
        file_size = os.path.getsize(path)
        file_time = os.path.getmtime(path)
        file_time_utc = datetime.fromtimestamp(file_time, tz=timezone.utc)
        backup_file_dto = S3BackupFileDTO(
            path='',
            file_name=file_name,
            file_size=file_size,
            file_time=file_time_utc,
        )
        file_info_list.append(backup_file_dto)

    else:
        raise FileNotFoundError(f"Path '{path}' does not exist or is not a file/directory.")

    return file_info_list


@pytest.fixture
def fill_db_with_backed_up_files():

    with Session() as session:
        backup_config = BackupConfig()
        for backup_storage in backup_config.backup_storages:
            for item in backup_storage.items:
                storage_orm = S3StorageOrm(
                    name=backup_storage.name,
                    url=item.url,
                    access_key=item.access_key,
                    storage_key=item.storage_key,
                )
                session.add(storage_orm)
                session.flush()

                files = get_backup_files_info(item.path, item.include, item.exclude)
                for file in files:
                    backup_file_orm = BackupFileOrm(
                        storage_id=storage_orm.id,
                        path=file.path,
                        file_name=file.filename,
                        file_size=file.file_size,
                        file_time=file.file_time,
                    )
                    session.add(backup_file_orm)
                    session.flush()
        session.commit()
