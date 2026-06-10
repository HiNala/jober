import asyncio
import io
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import BinaryIO

from minio import Minio

from jober_api.config import settings


@dataclass(frozen=True)
class StoredObject:
    bucket: str
    key: str
    etag: str | None


class ObjectStorage:
    """MinIO wrapper with presigned URL helpers."""

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket: str | None = None,
        secure: bool | None = None,
    ) -> None:
        self._bucket = bucket or settings.minio_bucket
        minio_kwargs: dict[str, object] = {}
        if settings.minio_region:
            minio_kwargs["region"] = settings.minio_region
        self._client = Minio(
            endpoint or settings.minio_endpoint,
            access_key=access_key or settings.minio_access_key,
            secret_key=secret_key or settings.minio_secret_key,
            secure=secure if secure is not None else settings.minio_secure,
            **minio_kwargs,  # type: ignore[arg-type]
        )

    @property
    def bucket(self) -> str:
        return self._bucket

    async def put_object(
        self,
        key: str,
        data: bytes | BinaryIO,
        content_type: str = "application/octet-stream",
        length: int | None = None,
    ) -> StoredObject:
        def _put() -> StoredObject:
            payload: BinaryIO
            size: int
            if isinstance(data, bytes):
                payload = io.BytesIO(data)
                size = length if length is not None else len(data)
            else:
                payload = data
                if length is None:
                    pos = payload.tell()
                    payload.seek(0, io.SEEK_END)
                    size = payload.tell()
                    payload.seek(pos)
                else:
                    size = length
            result = self._client.put_object(
                self._bucket,
                key,
                payload,
                size,
                content_type=content_type,
            )
            return StoredObject(bucket=self._bucket, key=key, etag=result.etag)

        return await asyncio.to_thread(_put)

    async def presigned_get(
        self,
        key: str,
        expires: timedelta | None = None,
    ) -> str:
        if expires is None:
            expires = timedelta(minutes=settings.presigned_url_ttl_minutes)
        return await asyncio.to_thread(
            self._client.presigned_get_object,
            self._bucket,
            key,
            expires=expires,
        )

    async def presigned_put(
        self,
        key: str,
        expires: timedelta | None = None,
    ) -> str:
        if expires is None:
            expires = timedelta(minutes=settings.presigned_url_ttl_minutes)
        return await asyncio.to_thread(
            self._client.presigned_put_object,
            self._bucket,
            key,
            expires=expires,
        )

    async def get_bytes(self, key: str) -> bytes:
        def _get() -> bytes:
            response = self._client.get_object(self._bucket, key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        return await asyncio.to_thread(_get)

    async def remove_object(self, key: str) -> None:
        await asyncio.to_thread(self._client.remove_object, self._bucket, key)

    async def bucket_exists(self) -> bool:
        return await asyncio.to_thread(self._client.bucket_exists, self._bucket)

    async def list_object_keys(self, prefix: str) -> list[str]:
        def _list() -> list[str]:
            objects = self._client.list_objects(self._bucket, prefix=prefix)
            return [obj.object_name for obj in objects]

        return await asyncio.to_thread(_list)

    async def remove_prefix(self, prefix: str) -> int:
        keys = await self.list_object_keys(prefix)
        for key in keys:
            await self.remove_object(key)
        return len(keys)


def new_upload_key(prefix: str, suffix: str = "") -> str:
    return f"{prefix}/{uuid.uuid4()}{suffix}"
