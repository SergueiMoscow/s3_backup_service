from common.schemas import BucketDTO, S3StorageDTO, BucketAddDTO
from db.engine import Session
from db.models import BucketOrm
from repositories.buckets import get_bucket_by_storage_and_path_repository, create_bucket
from repositories.s3_storages import get_storage_by_id


async def get_bucket_by_storage_and_path(s3_storage_id: int, path: str) -> BucketOrm | None:
    with Session() as session:
        bucket = get_bucket_by_storage_and_path_repository(
            session=session,
            storage_id=s3_storage_id,
            path=path,
        )
        return bucket


def create_bucket_service(
        bucket: BucketAddDTO,
        storage_id: int,
) -> BucketDTO:
    with Session() as session:
        storage = get_storage_by_id(session=session, storage_id=storage_id)
        bucket_orm = BucketOrm(storage=storage, **BucketDTO.model_dump(bucket))
        create_bucket(session, bucket_orm)
        session.commit()
        result = BucketDTO.model_validate(bucket_orm, from_attributes=True)
    return result


def create_or_get_bucket_by_storage_and_path(s3_storage: S3StorageDTO, path: str) -> BucketDTO:
    with Session() as session:
        bucket_orm = get_bucket_by_storage_and_path_repository(
            session=session,
            storage_id=s3_storage.id,
            path=path,
        )
        if bucket_orm is not None:
            return BucketDTO.model_validate(bucket_orm, from_attributes=True)
        bucket_dto = BucketAddDTO(storage_id=s3_storage.id, path=path)
        return create_bucket_service(bucket=bucket_dto, storage_id=s3_storage.id)
