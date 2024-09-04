from sqlalchemy import update, and_, select, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db.models import BackupFileOrm


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


def get_backup_file_by_path_and_name(session: Session, full_path: str, name: str) -> BackupFileOrm | None:
    return session.query(BackupFileOrm).filter(
        and_(
            func.concat(BackupFileOrm.item_path, BackupFileOrm.path) == full_path,
            BackupFileOrm.name == name,
        )
    ).one_or_none()


def get_backup_file_by_details(session: Session, storage_id: int, item_id: int, path: str, file_name: str) -> BackupFileOrm | None:
    """
    Возвращает экземпляр BackupFileOrm по указанным параметрам.

    :param session: Объект сессии SQLAlchemy.
    :param storage_id: Идентификатор хранилища.
    :param path: Путь к файлу.
    :param file_name: Имя файла.
    :return: Экземпляр BackupFileOrm.
    :raises NoResultFound: Если не найден ни один файл с указанными параметрами.
    """
    backup_file = session.query(BackupFileOrm).filter_by(
        storage_id=storage_id,
        item_id = item_id,
        path=path,
        file_name=file_name
    ).one_or_none()
    return backup_file


def get_backed_up_item_info(session: Session, storage_id: int, item_id: int):
    """

    :param session:
    :param storage_id:
    :param item_id:
    :return:
    """
    ...
