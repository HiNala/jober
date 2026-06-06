import os
import uuid

import pytest

from jober_api.storage.keys import resume_key
from jober_api.storage.minio_client import ObjectStorage


@pytest.mark.asyncio
async def test_presigned_put_get_round_trip() -> None:
    if os.getenv("CI") != "true" and os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("requires MinIO (CI or RUN_INTEGRATION=1)")

    storage = ObjectStorage()
    asset_id = uuid.uuid4()
    key = resume_key(asset_id, "resume.pdf")
    body = b"%PDF-1.4 jober test resume"

    await storage.put_object(key, body, content_type="application/pdf")
    put_url = await storage.presigned_put(key)
    get_url = await storage.presigned_get(key)

    assert key in put_url
    assert key in get_url or asset_id.hex in get_url

    downloaded = await storage.get_bytes(key)
    assert downloaded == body

    await storage.remove_object(key)
