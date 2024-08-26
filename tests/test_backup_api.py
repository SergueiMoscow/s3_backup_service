from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.app import app
from common import BackupConfig
from common.settings import settings

# client = TestClient(app)

@pytest.mark.asyncio
@pytest.mark.usefixtures('apply_migrations')
@patch("services.S3Client.S3Client.get_client")
async def test_post_backup_success(mock_get_client):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        mock_s3_client = AsyncMock()
        mock_get_client.return_value.__aenter__.return_value = mock_s3_client
        backup_config = BackupConfig.BackupConfig().get_settings()
        response = await client.post(
            "/backup",
            headers={"api_key": settings.API_KEY},
            json={
                "storage": backup_config['s3_storages'][0]['name'],
                "item": backup_config['s3_storages'][0]['items'][0]['name']},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

# Тестирование запроса без API_KEY
@pytest.mark.asyncio
async def test_post_backup_missing_api_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/backup",
            json={"storage": "example_storage", "item": "example_item"}
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Доступ запрещён"}

# Тестирование запроса с некорректным API_KEY
@pytest.mark.asyncio
async def test_post_backup_invalid_api_key():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/backup",
            json={"storage": "example_storage", "item": "example_item"},
            headers={"API_KEY": "invalid_api_key"}
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Доступ запрещён"}
