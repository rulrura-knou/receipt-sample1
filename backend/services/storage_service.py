from __future__ import annotations

import json
import os
from datetime import datetime

from backend.config import (
    RECEIPTS_FILE, USE_VERCEL_KV,
    KV_REST_API_URL, KV_REST_API_TOKEN,
)
from backend.models.receipt import Receipt

_KV_KEY = "receipts"

if USE_VERCEL_KV:
    from upstash_redis.asyncio import Redis as _AsyncRedis
    _redis = _AsyncRedis(url=KV_REST_API_URL, token=KV_REST_API_TOKEN)


async def _read_all() -> list[dict]:
    if USE_VERCEL_KV:
        data = await _redis.get(_KV_KEY)
        return json.loads(data) if data else []
    if not os.path.exists(RECEIPTS_FILE):
        return []
    import aiofiles
    async with aiofiles.open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
    return json.loads(content) if content.strip() else []


async def _write_all(receipts: list[dict]) -> None:
    if USE_VERCEL_KV:
        await _redis.set(_KV_KEY, json.dumps(receipts, ensure_ascii=False, default=str))
        return
    import aiofiles
    async with aiofiles.open(RECEIPTS_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(receipts, ensure_ascii=False, indent=2, default=str))


async def list_receipts() -> list[dict]:
    return await _read_all()


async def get_receipt(receipt_id: str) -> dict | None:
    receipts = await _read_all()
    return next((r for r in receipts if r["id"] == receipt_id), None)


async def create_receipt(receipt: Receipt) -> dict:
    receipts = await _read_all()
    data = receipt.model_dump()
    receipts.append(data)
    await _write_all(receipts)
    return data


async def update_receipt(receipt_id: str, updates: dict) -> dict | None:
    receipts = await _read_all()
    for i, r in enumerate(receipts):
        if r["id"] == receipt_id:
            receipts[i].update(updates)
            receipts[i]["updated_at"] = datetime.now().isoformat()
            await _write_all(receipts)
            return receipts[i]
    return None


async def delete_receipt(receipt_id: str) -> bool:
    receipts = await _read_all()
    filtered = [r for r in receipts if r["id"] != receipt_id]
    if len(filtered) == len(receipts):
        return False
    await _write_all(filtered)
    return True
