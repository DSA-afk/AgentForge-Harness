from minio import Minio
from app.config.config import settings


class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )

    def ensure_bucket(self, bucket_name: str):
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
        else:
            print(f"Bucket {bucket_name} 已存在")

    def upload_file(self, up_file: dict,data,length,content_type):
        key = f"{up_file['tenant_id']}/{up_file['document_id']}/{up_file['file_name']}"
        result = self.client.put_object(
            up_file['bucket_name'],
            key,
            data = data,
            length = length,
            content_type = content_type
        )
        return result.object_name


minio_client = MinioClient()