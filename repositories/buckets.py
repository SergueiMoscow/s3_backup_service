from db.engine import Session
from db.models import BackupFileOrm, BucketOrm


def create_bucket(session: Session, bucket: BucketOrm) -> BucketOrm:
    session.add(bucket)
    return bucket


def get_bucket_by_id(session: Session, bucket_id: int) -> BucketOrm | None:
    return session.query(BucketOrm).filter(BucketOrm.id == bucket_id).one_or_none()


def get_bucket_by_storage_and_path_repository(session: Session, storage_id: int, path: str) -> BucketOrm | None:
    return session.query(BucketOrm).filter_by(
        storage_id=storage_id,
        path=path,
    ).one_or_none()
