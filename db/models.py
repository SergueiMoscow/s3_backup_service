from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import declarative_base, backref, Mapped, mapped_column, relationship
from typing import Annotated


STRING_255 = 255
STRING_32 = 32

Base = declarative_base()

LAZY_TYPE = 'select'

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


class S3StorageOrm(Base):
    __tablename__ = 's3_storages'
    id: Mapped[int] = mapped_column(primary_key=True)
    name = mapped_column(String(STRING_32), nullable=False, index=True)
    url = mapped_column(String(STRING_255), nullable=False)
    access_key = mapped_column(String(STRING_255), nullable=False)
    secret_key = mapped_column(String(STRING_255), nullable=False)
    created_at = mapped_column(DateTime, default=func.now())

    buckets: Mapped[list['BucketOrm']] = relationship(
        'BucketOrm',
        back_populates='storage',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    files: Mapped[list['BackupFileOrm']] = relationship(
        'BackupFileOrm',
        back_populates='storage',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    def __repr__(self):
        return f"S3StorageOrm(id={self.id}, name='{self.name}', url='{self.url}')"

    __table_args__ = (
        Index('idx_s3storage_name', 'name'),
    )


class BucketOrm(Base):
    __tablename__ = 'buckets'
    id: Mapped[int] = mapped_column(primary_key=True)
    storage_id = mapped_column(ForeignKey('s3_storages.id', ondelete='CASCADE'), nullable=False)
    path = mapped_column(String(STRING_255), nullable=False)

    storage: Mapped['S3StorageOrm'] = relationship('S3StorageOrm', back_populates='buckets')
    files: Mapped[list['BackupFileOrm']] = relationship(
        'BackupFileOrm',
        back_populates='bucket',
        cascade='all, delete-orphan',
        lazy='selectin'
    )


class BackupFileOrm(Base):
    __tablename__ = 'backup_files'
    id: Mapped[int] = mapped_column(primary_key=True)
    storage_id = mapped_column(ForeignKey('s3_storages.id', ondelete='CASCADE'), nullable=False)
    bucket_id = mapped_column(ForeignKey('buckets.id', ondelete='CASCADE'), nullable=False)
    path = mapped_column(String(STRING_255), nullable=False)
    file_name = mapped_column(String(STRING_255), nullable=False)
    file_size = mapped_column(Integer, nullable=False)
    file_time = mapped_column(DateTime, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())

    storage: Mapped['S3StorageOrm'] = relationship('S3StorageOrm', back_populates='files')
    bucket: Mapped['BucketOrm'] = relationship('BucketOrm', back_populates='files')

    def __repr__(self):
        return f"BackupFileOrm(id={self.id}, file_name='{self.file_name}', file_size={self.file_size})"

    __table_args__ = (
        Index('idx_bucket_file_name', 'storage_id', 'bucket_id', 'path', 'file_name'),
    )
