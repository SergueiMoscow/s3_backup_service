from schemas import BackupItem
from common import BackupConfig


def test_backup_config():
    backup_config = BackupConfig.BackupConfig()
    assert backup_config is not None
    assert backup_config.backup_storages[0].items is not None

def test_read_directory():
    pass
    # assert backup_config.backup_storages[0].items[0] is not None
    # assert isinstance(backup_config.backup_storages[0].items[0], BackupItem)
