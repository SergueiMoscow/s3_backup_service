import asyncio

from common.BackupConfig import BackupConfig
from services.backup import backup

if __name__ == '__main__':
    asyncio.run(backup())
