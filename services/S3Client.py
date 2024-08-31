from contextlib import asynccontextmanager

from aiobotocore.session import get_session, ClientCreatorContext
from botocore.exceptions import ClientError
from fastapi import HTTPException

from api.exceptions import S3BucketError
from api.websocket import ConnectionManager


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
    ):
        self.config = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'endpoint_url': endpoint_url,
        }
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> ClientCreatorContext:
        async with self.session.create_client("s3", verify=False, **self.config) as client:
            yield client

    async def upload_file(
        self,
        bucket_name: str,
        file_path: str,
        object_name: str,
        socket_manager: ConnectionManager | None,
    ):
        async with self.get_client() as client:
            try:
                with open(file_path, 'rb') as file:
                    await client.put_object(
                        Bucket=bucket_name,
                        Key=object_name,
                        Body=file,
                    )
            except ClientError as e:
                if socket_manager is not None:
                    await socket_manager.send_message(f'Error on upload file {e.response}')
                raise S3BucketError(
                    status_code=400,
                    detail=e.response
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

