from common.schemas import BackupItem
from common import BackupConfig


def test_backup_config():
    backup_config = BackupConfig.BackupConfig()
    assert backup_config is not None
    assert backup_config.backup_storages[0].items is not None
