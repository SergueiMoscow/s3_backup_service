import copy
import os

from db.engine import Session
from db.models import S3StorageOrm, BackupFileOrm
from repositories.backup_files import create_backup_file, get_backup_file_by_id, update_backup_file, \
    get_backup_file_by_details
from repositories.s3_storages import create_storage, update_storage, get_storage_by_id, delete_storage
from schemas import S3StorageDTO, BackupItem, S3BackupFileDTO, S3BackupFileRelDTO
from services.Encryption import encryption_service
from services.s3_storages import decrypt_storage

fields_to_encrypt = ('url', 'access_key', 'secret_key')



def create_s3_backup_file_service(
        backup_file: S3BackupFileDTO,
        storage: S3StorageOrm | None = None,
        storage_id: int | None = None,
) -> S3BackupFileDTO:
    """Передавать либо storage (модель) либо storage_id (int)."""
    with Session() as session:
        if storage_id is not None and storage is None:
            storage = get_storage_by_id(session=session, storage_id=storage_id)
        backup_file_model = BackupFileOrm(storage=storage, **S3BackupFileDTO.model_dump(backup_file))

        create_backup_file(session, backup_file_model)
        session.commit()
        result = S3BackupFileDTO.model_validate(backup_file_model, from_attributes=True)
    return result


def update_s3_backup_file_service(backup_file_id: int, s3_backup_file_updated: S3BackupFileDTO) -> S3BackupFileDTO:
    with Session() as session:
        s3_backup_file = get_backup_file_by_id(session, backup_file_id)
        if s3_backup_file is None:
            raise ValueError("s3_backup_file_model not found with id: %s" % backup_file_id)
        return update_backup_file(session, backup_file_id, s3_backup_file_updated.model_dump())


def get_backup_file_by_details_service(storage_id: int, path: str, file_name: str) -> S3BackupFileDTO | None:
    with Session() as session:
        backup_file_orm = get_backup_file_by_details(
            session=session,
            storage_id=storage_id,
            path=path,
            file_name=file_name,
        )
        if backup_file_orm is not None:
            backup_file_dto = S3BackupFileDTO.model_validate(backup_file_orm, from_attributes=True)
            return backup_file_dto
        return None


def delete_storage_service(s3_storage_id: int) -> None:
    with Session() as session:
        s3_storage = get_storage_by_id(session, s3_storage_id)
        delete_storage(s3_storage)
