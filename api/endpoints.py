from fastapi import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from common.BackupConfig import BackupConfig
from common.schemas import BasicBackupStorage, BackupDTO
from services.backup import backup
from services.verify_api_key import verify_api_key
from fastapi import APIRouter
import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=FORMAT)

router = APIRouter()


@router.get('/config', response_model=list[BasicBackupStorage])
def get_config(api_key: str = Depends(verify_api_key)):
    config = BackupConfig()
    settings = config.get_settings()
    return [BasicBackupStorage(**storage) for storage in settings['s3_storages']]


@router.post('/backup')
async def run_backup(
    data: BackupDTO,
    api_key: str = Depends(verify_api_key)
):
    logger.info(f'Running backup({data.storge}, {data.item}')
    await backup(storage_name=data.storage, item_name=data.item)
    return {"status": "success"}
