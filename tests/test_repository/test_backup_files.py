import os

import pytest

from db.engine import Session
from repositories.backup_files import list_backed_up_files


@pytest.mark.usefixtures('apply_migrations')
def test_list_backed_up_files(created_backup_file):
    with Session() as session:
        files = list_backed_up_files(session=session, storage_id=1, bucket_id=1)
    assert files[0].path == os.path.join(created_backup_file.bucket.path, created_backup_file.path, created_backup_file.file_name)
    assert files[0].size == created_backup_file.file_size
    assert files[0].time == created_backup_file.file_time
