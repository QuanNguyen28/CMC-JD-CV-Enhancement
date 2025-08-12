from __future__ import annotations
from typing import Optional, Tuple
from datetime import timedelta
import io
import re

from minio import Minio
from minio.error import S3Error

from src.core.config import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
    MINIO_SECURE, MINIO_DEFAULT_BUCKET
)

_client: Optional[Minio] = None

def get_minio() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=bool(MINIO_SECURE),
        )
    return _client

def ensure_bucket(bucket: Optional[str] = None) -> str:
    bucket = bucket or MINIO_DEFAULT_BUCKET
    cli = get_minio()
    found = cli.bucket_exists(bucket)
    if not found:
        cli.make_bucket(bucket)
    return bucket

def object_exists(bucket: str, key: str) -> bool:
    try:
        get_minio().stat_object(bucket, key)
        return True
    except S3Error:
        return False

def _parse_key_or_url(key_or_url: str, default_bucket: Optional[str] = None) -> Tuple[str, str]:
    """
    Hỗ trợ các dạng:
      - "bucket/key/abc.md"
      - "minio://bucket/key/abc.md"
      - "s3://bucket/key/abc.md"
      - "http(s)://<endpoint>/<bucket>/<key...>"  (nếu bạn lưu full URL)
    """
    s = key_or_url.strip()
    # s3/minio scheme
    m = re.match(r'^(s3|minio)://([^/]+)/(.+)$', s, re.IGNORECASE)
    if m:
        return m.group(2), m.group(3)

    # http(s)://endpoint/bucket/key...
    m = re.match(r'^https?://[^/]+/([^/]+)/(.+)$', s, re.IGNORECASE)
    if m:
        return m.group(1), m.group(2)

    # bucket/key...
    if "/" in s:
        bucket, key = s.split("/", 1)
        return bucket, key

    # chỉ có key, dùng default bucket
    return (default_bucket or MINIO_DEFAULT_BUCKET), s

def get_object_str(key_or_url: str, *, bucket: Optional[str] = None, encoding: str = "utf-8") -> str:
    """
    Đọc object và trả về chuỗi UTF-8.
    """
    if not key_or_url:
        return ""
    bkt, key = _parse_key_or_url(key_or_url, default_bucket=bucket or MINIO_DEFAULT_BUCKET)
    try:
        resp = get_minio().get_object(bkt, key)
        try:
            data = resp.read()
            return data.decode(encoding, errors="ignore")
        finally:
            resp.close()
            resp.release_conn()
    except S3Error as e:
        # Tuỳ nhu cầu, có thể raise
        return ""

def put_object_str(bucket: str, key: str, text: str, encoding: str = "utf-8") -> None:
    data = text.encode(encoding)
    get_minio().put_object(
        bucket_name=ensure_bucket(bucket),
        object_name=key,
        data=io.BytesIO(data),
        length=len(data),
        content_type="text/plain; charset=utf-8",
    )

def get_presigned_url(bucket: str, key: str, expires_seconds: int = 3600) -> str:
    return get_minio().presigned_get_object(
        bucket_name=bucket,
        object_name=key,
        expires=timedelta(seconds=expires_seconds),
    )