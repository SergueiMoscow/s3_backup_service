from fastapi import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from common.BackupConfig import BackupConfig
from common.schemas import BasicBackupStorage, BackupDTO
from services.backup import backup
from services.get_item_info import get_bucket_info_service
from services.verify_api_key import verify_api_key
from fastapi import APIRouter
import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=logging.INFO, format=FORMAT)

router = APIRouter()
logger = logging.getLogger(__name__)


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
    logger.info(f'Running backup({data.storage}, {data.item}')
    await backup(storage_name=data.storage, item_name=data.item)
    return {"status": "success"}


@router.get('/info')
async def get_item_info(
    data: BackupDTO,
    api_key: str = Depends(verify_api_key)
):
    return await get_bucket_info_service(data=data)
