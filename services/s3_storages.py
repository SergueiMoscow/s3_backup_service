import copy

from db.engine import Session
from db.models import S3StorageOrm
from repositories.s3_storages import create_storage, update_storage, get_storage_by_id, delete_storage, \
    get_storage_by_name
from schemas import S3StorageDTO
from services.Encryption import encryption_service

fields_to_encrypt = ('url', 'access_key', 'secret_key')


def encrypt_storage(s3_storage: S3StorageOrm | S3StorageDTO) -> S3StorageOrm | S3StorageDTO:
    # Работаем с копией объекта
    encrypted_s3_storage = copy.deepcopy(s3_storage)

    # Шифрование
    for field in fields_to_encrypt:
        value = getattr(s3_storage, field)
        encrypted_value = encryption_service.encrypt(value)
        setattr(encrypted_s3_storage, field, encrypted_value)
    return encrypted_s3_storage


def decrypt_storage(s3_storage: S3StorageOrm | S3StorageDTO) -> S3StorageOrm | S3StorageDTO:
    # Дешифрование
    for field in fields_to_encrypt:
        value = getattr(s3_storage, field)
        encrypted_value = encryption_service.decrypt(value)
        setattr(s3_storage, field, encrypted_value)
    return s3_storage


def create_s3_storage_service(s3_storage: S3StorageDTO) -> S3StorageDTO:
    s3_storage_dict = s3_storage.model_dump()
    s3_storage_model = S3StorageOrm(**s3_storage_dict)
    encrypted_s3_storage_model = encrypt_storage(s3_storage_model)
    with Session() as session:
        create_storage(session, encrypted_s3_storage_model)
        session.flush()
        if encrypted_s3_storage_model.id is None:
            raise ValueError('Cannot create s3_storage')
        result = S3StorageDTO.model_validate(s3_storage_model, from_attributes=True)
        result.id = encrypted_s3_storage_model.id
        session.commit()
    # Возвращаем объект БЕЗ шифрования
    return result


def update_s3_storage_service(s3_storage_id: int, s3_storage: S3StorageDTO) -> S3StorageOrm:
    with Session() as session:
        s3_storage_model = get_storage_by_id(session, s3_storage_id)
        if s3_storage_model is None:
            raise ValueError("s3_storage_model not found with id: %s" % s3_storage_id)
        encrypted_s3_storage = encrypt_storage(s3_storage)
        return update_storage(session, s3_storage_id, encrypted_s3_storage.model_dump())


def get_s3_storage_by_id_service(s3_storage_id: int) -> S3StorageOrm | None:
    with Session() as session:
        s3_storage = get_storage_by_id(session, s3_storage_id)
        decrypted_s3_storage = decrypt_storage(s3_storage)
        return decrypted_s3_storage


def delete_storage_service(s3_storage_id: int) -> None:
    with Session() as session:
        s3_storage = get_storage_by_id(session, s3_storage_id)
        delete_storage(s3_storage)


def create_or_get_storage_by_name(s3_storage: S3StorageDTO) -> S3StorageDTO:
    with Session() as session:
        storage_orm = get_storage_by_name(session, s3_storage.name)
        if storage_orm is not None:
            return S3StorageDTO.model_validate(storage_orm, from_attributes=True)
    return create_s3_storage_service(s3_storage)
