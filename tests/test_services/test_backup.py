from common.BackupConfig import BackupConfig
from services.backup import backup, backup_item

import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
@pytest.mark.usefixtures('apply_migrations')
@patch("services.S3Client.S3Client.get_client")
async def test_upload_file(mock_get_client):
    mock_s3_client = AsyncMock()
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client
    await backup()
    mock_s3_client.put_object.assert_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures()
async def test_files_uploaded():
    with patch('services.S3Client.S3Client.get_client') as mock_get_client:
        mock_s3_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client
        await backup()
        mock_s3_client.put_object.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures('apply_migrations')
@patch("services.backup.backup_item")
async def test_backup_item(mock_backup_item):
    backup_config = BackupConfig().get_settings()
    await backup(
        storage_name=backup_config['s3_storages'][0]['name'],
        item_name=backup_config['s3_storages'][0]['items'][0]['name'],
    )
    mock_backup_item.assert_called_once()
