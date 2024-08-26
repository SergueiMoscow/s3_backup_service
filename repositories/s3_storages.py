from sqlalchemy import update, select
from sqlalchemy.orm import Session

from db.models import S3StorageOrm
from schemas import S3StorageAddDTO


def create_storage(session: Session, storage: S3StorageOrm) -> S3StorageOrm:
    session.add(storage)
    return storage


def update_storage(session: Session, storage_id: int, update_data: dict):
    storage = session.scalar(select(S3StorageOrm).where(S3StorageOrm.id == storage_id))
    if not storage:
        return None
    for key, value in update_data.items():
        setattr(storage, key, value)
    session.commit()
    return storage


def get_storage_by_id(session: Session, storage_id: int) -> S3StorageOrm | None:
    return session.query(S3StorageOrm).filter(S3StorageOrm.id == storage_id).one_or_none()


def get_storage_by_name(session: Session, storage_name: str) -> S3StorageOrm | None:
    return session.query(S3StorageOrm).filter(S3StorageOrm.name == storage_name).one_or_none()


def delete_storage(session: Session, storage_model: S3StorageOrm) -> None:
    session.delete(storage_model)
