"""MinIO 对象存储客户端。"""
from __future__ import annotations


class MinIOStorage:
    """MinIO 文件存储（简化实现，生产环境使用 minio-py）。"""

    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket

    async def upload(self, object_name: str, data: bytes, content_type: str = "") -> str:
        """上传文件，返回访问 URL。"""
        # 生产环境：使用 minio-py 的 async client
        return f"http://{self.endpoint}/{self.bucket}/{object_name}"

    async def download(self, object_name: str) -> bytes:
        """下载文件。"""
        return b""