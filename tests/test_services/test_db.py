import pytest
from sqlalchemy import select

from db.engine import Session
from db.models import S3StorageOrm, BackupFileOrm
from schemas import S3StorageDTO, S3BackupFileDTO
from services.backup_files import create_s3_backup_file_service
from services.s3_storages import create_s3_storage_service, update_s3_storage_service, get_s3_storage_by_id_service, \
    create_or_get_storage_by_name


@pytest.mark.usefixtures('apply_migrations')
def test_create_s3_storage(s3_storage_schema):
    created_storage = create_s3_storage_service(s3_storage_schema)
    with Session() as session:
        check_created_storage = session.scalar(select(S3StorageOrm).where(S3StorageOrm.id == created_storage.id))
        assert created_storage.id == check_created_storage.id


@pytest.mark.usefixtures('apply_migrations')
def test_create_and_read_s3_storage(s3_storage_schema):
    created_storage = create_s3_storage_service(s3_storage_schema)
    read_storage = get_s3_storage_by_id_service(s3_storage_id=created_storage.id)
    assert created_storage.name == read_storage.name
    assert created_storage.access_key == read_storage.access_key
    assert created_storage.secret_key == read_storage.secret_key


@pytest.mark.usefixtures('apply_migrations')
def test_update_s3_storage(created_s3_storage_dto, faker):
    updated_name = faker.address()
    created_s3_storage_dto.name = updated_name
    storage_id = created_s3_storage_dto.id
    update_s3_storage_service(
        s3_storage_id=storage_id,
        s3_storage=created_s3_storage_dto,
    )
    with Session() as session:
        updated_s3_storage = session.scalar(select(S3StorageOrm).where(S3StorageOrm.id == storage_id))
    assert updated_s3_storage.name == updated_name


@pytest.mark.usefixtures('apply_migrations')
def test_create_backup_file(created_s3_storage_orm, s3_backup_file_schema):
    created_s3_backup_file = create_s3_backup_file_service(s3_backup_file_schema, created_s3_storage_orm)
    with Session() as session:
        check_created_backup_file = session.scalar(select(BackupFileOrm).where(BackupFileOrm.id == created_s3_backup_file.id))
        assert created_s3_backup_file.id == check_created_backup_file.id


@pytest.mark.usefixtures('apply_migrations')
def test_create_or_get_storage_by_name_found(created_s3_storage_dto):
    found_storage = create_or_get_storage_by_name(created_s3_storage_dto)
    assert found_storage.id == created_s3_storage_dto.id
    assert found_storage.url == created_s3_storage_dto.url


@pytest.mark.usefixtures('apply_migrations')
def test_create_or_get_storage_by_name_not_found(s3_storage_schema):
    found_storage = create_or_get_storage_by_name(s3_storage_schema)
    assert found_storage.name == s3_storage_schema.name
    assert found_storage.url == s3_storage_schema.url
    assert found_storage.id is not None