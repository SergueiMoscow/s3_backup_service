from fastapi import APIRouter, Depends

from common.BackupConfig import BackupConfig
from schemas import BackupStorage, BasicBackupStorage, BackupDTO
from services.backup import backup
from services.verify_api_key import verify_api_key

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
    await backup(storage_name=data.storage, item_name=data.item)
    return {"status": "success"}
