from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol
from uuid import uuid4


class MediaStore(Protocol):
    name: str
    durable: bool

    def save(self, data: bytes, content_type: str, extension: str) -> str: ...
    def describe(self) -> dict: ...


class LocalMediaStore:
    name = "LOCAL_MEDIA"
    durable = False

    def __init__(self, root: Path, public_prefix: str = "/market/media"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.public_prefix = public_prefix.rstrip("/")

    def save(self, data: bytes, content_type: str, extension: str) -> str:
        filename = f"MED-{uuid4().hex[:20].upper()}{extension}"
        (self.root / filename).write_bytes(data)
        return f"{self.public_prefix}/{filename}"

    def describe(self) -> dict:
        return {
            "name": self.name,
            "durable": self.durable,
            "scope": "prototype",
            "note": "Local service files are a prototype fallback. Set S3-compatible media environment variables for durable object storage without changing listing contracts.",
        }


class S3MediaStore:
    name = "S3_COMPATIBLE_MEDIA"
    durable = True

    def __init__(
        self,
        *,
        bucket: str,
        public_base_url: str,
        region: str | None = None,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        import boto3

        kwargs = {
            "service_name": "s3",
            "region_name": region or None,
            "endpoint_url": endpoint_url or None,
        }
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key
        self.client = boto3.client(**kwargs)
        self.bucket = bucket
        self.public_base_url = public_base_url.rstrip("/")

    def save(self, data: bytes, content_type: str, extension: str) -> str:
        key = f"marketplace/{uuid4().hex[:2]}/{uuid4().hex}{extension}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl="public,max-age=31536000,immutable",
        )
        return f"{self.public_base_url}/{key}"

    def describe(self) -> dict:
        return {
            "name": self.name,
            "durable": self.durable,
            "scope": "production-ready-adapter",
            "bucket": self.bucket,
            "public_base_url": self.public_base_url,
        }


def media_store_from_env(root: Path) -> MediaStore:
    bucket = os.getenv("CARBON_MEDIA_S3_BUCKET", "").strip()
    public_base = os.getenv("CARBON_MEDIA_PUBLIC_BASE_URL", "").strip()
    if bucket and public_base:
        return S3MediaStore(
            bucket=bucket,
            public_base_url=public_base,
            region=os.getenv("CARBON_MEDIA_S3_REGION", "").strip() or None,
            endpoint_url=os.getenv("CARBON_MEDIA_S3_ENDPOINT", "").strip() or None,
            access_key=os.getenv("CARBON_MEDIA_S3_ACCESS_KEY", "").strip() or None,
            secret_key=os.getenv("CARBON_MEDIA_S3_SECRET_KEY", "").strip() or None,
        )
    local_dir = Path(os.getenv("CARBON_MARKETPLACE_MEDIA_DIR") or root / "data/carbon_media")
    return LocalMediaStore(local_dir)
