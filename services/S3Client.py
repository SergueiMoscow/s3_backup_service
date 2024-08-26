from contextlib import asynccontextmanager

from aiobotocore.session import get_session, ClientCreatorContext


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
    ):
        async with self.get_client() as client:
            with open(file_path, 'rb') as file:
                await client.put_object(
                    Bucket=bucket_name,
                    Key=object_name,
                    Body=file,
                )
