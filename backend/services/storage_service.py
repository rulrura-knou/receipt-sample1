from __future__ import annotations

import json
import os
from datetime import datetime

import aiofiles

from backend.config import RECEIPTS_FILE
from backend.models.receipt import Receipt


async def _read_all() -> list[dict]:
    if not os.path.exists(RECEIPTS_FILE):
        return []
    async with aiofiles.open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
    return json.loads(content) if content.strip() else []


async def _write_all(receipts: list[dict]) -> None:
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
