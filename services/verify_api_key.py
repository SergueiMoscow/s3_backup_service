from typing import Optional

from fastapi import Header, HTTPException
from common.settings import settings


async def verify_api_key(api_key: Optional[str] = Header(None, alias='api_key')):
    if api_key is None or api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
