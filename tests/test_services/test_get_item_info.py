import os
from datetime import datetime
from pathlib import Path

import pytest

from common.schemas import FileInfo, BackupDTO
from services.get_item_info import list_files_recursive, get_bucket_info_service
from tests.conftest import TEST_BACKUP_DIR


def test_list_files_recursive():
    extensions_include = ['png']
    real_files = os.scandir(TEST_BACKUP_DIR)
    expected_result = []
    for entry in real_files:
        _, extension = os.path.splitext(entry)
        extension = extension.lower().replace('.', '')
        if entry.is_file() and extension in extensions_include:
            expected_result.append(FileInfo(
                path=os.path.join(TEST_BACKUP_DIR, entry),
                size=os.path.getsize(entry.path),
                time=datetime.fromtimestamp(os.path.getmtime(entry.path)),
            ))
    result = list_files_recursive(TEST_BACKUP_DIR, ['png'])
    assert result
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.usefixtures('apply_migrations')
async def test_get_bucket_info_service_empty_db(backup_config):
    first_config_storage = backup_config.backup_storages[0]
    first_config_item = first_config_storage.items[0]
    backup_dto = BackupDTO(
        storage = first_config_storage.name,
        item = first_config_item.name,
    )
    result = await get_bucket_info_service(data=backup_dto)
    assert result['deleted'] == []
    assert result['updated'] == []
    assert result['status'] == 'Ok'
    assert isinstance(result['new'], list)
    assert len(result['new']) > 0
