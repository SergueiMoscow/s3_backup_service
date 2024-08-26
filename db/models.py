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
    id: Mapped[intpk]
    name = Column(String(STRING_32), nullable=False, index=True)
    url = Column(String(STRING_255), nullable=False)
    access_key = Column(String(STRING_255), nullable=False)
    secret_key = Column(String(STRING_255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    files: Mapped[list['BackupFileOrm']] = relationship(
        back_populates='storage',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    def __repr__(self):
        return f"S3StorageOrm(id={self.id}, name='{self.name}', url='{self.url}')"

    __table_args__ = (
        Index('idx_s3storage_name', 'name'),
    )

class BackupFileOrm(Base):
    __tablename__ = 'backup_file'
    id: Mapped[intpk]
    storage_id = mapped_column(ForeignKey('s3_storages.id', ondelete='CASCADE'), nullable=False)
    path = Column(String(STRING_255), nullable=False)
    file_name = Column(String(STRING_255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    storage: Mapped['S3StorageOrm'] = relationship('S3StorageOrm', back_populates='files')

    def __repr__(self):
        return f"BackupFileOrm(id={self.id}, file_name='{self.file_name}', file_size={self.file_size})"

    __table_args__ = (
        Index('idx_storage_file_name', 'storage_id', 'file_name'),
    )