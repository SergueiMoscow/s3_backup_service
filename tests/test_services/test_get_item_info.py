import os
from datetime import datetime
from pathlib import Path

from common.schemas import FileInfo
from services.get_item_info import list_files_recursive
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
