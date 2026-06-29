from __future__ import annotations

import json
import os
from datetime import datetime

from backend.config import (
    DATABASE_URL, USE_NEON_DB,
    RECEIPTS_FILE, USE_VERCEL_KV,
    KV_REST_API_URL, KV_REST_API_TOKEN,
)
from backend.models.receipt import Receipt

# ── Neon PostgreSQL ──────────────────────────────────────────────────────────
_pg_pool = None


async def _get_pool():
    global _pg_pool
    import asyncpg
    if _pg_pool is None:
        _pg_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        async with _pg_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    store_name TEXT DEFAULT '',
                    date TEXT DEFAULT '',
                    total_amount INTEGER DEFAULT 0,
                    items JSONB DEFAULT '[]',
                    raw_ocr TEXT DEFAULT '',
                    image_filename TEXT DEFAULT '',
                    image_data BYTEA,
                    image_mime TEXT DEFAULT 'image/jpeg',
                    category TEXT DEFAULT '기타',
                    memo TEXT DEFAULT '',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            # 기존 테이블에 컬럼이 없을 경우 추가
            await conn.execute("""
                ALTER TABLE receipts
                    ADD COLUMN IF NOT EXISTS image_data BYTEA,
                    ADD COLUMN IF NOT EXISTS image_mime TEXT DEFAULT 'image/jpeg'
            """)
    return _pg_pool


def _row_to_dict(row) -> dict:
    d = dict(row)
    d.pop("image_data", None)   # 바이너리 데이터는 응답에서 제외
    if isinstance(d.get("items"), str):
        d["items"] = json.loads(d["items"])
    for key in ("created_at", "updated_at"):
        if d.get(key) and not isinstance(d[key], str):
            d[key] = d[key].isoformat()
    return d


# ── Vercel KV ────────────────────────────────────────────────────────────────
_KV_KEY = "receipts"

if USE_VERCEL_KV:
    from upstash_redis.asyncio import Redis as _AsyncRedis
    _redis = _AsyncRedis(url=KV_REST_API_URL, token=KV_REST_API_TOKEN)


# ── 로컬 파일 폴백 ────────────────────────────────────────────────────────────
async def _file_read_all() -> list[dict]:
    if not os.path.exists(RECEIPTS_FILE):
        return []
    import aiofiles
    async with aiofiles.open(RECEIPTS_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
    return json.loads(content) if content.strip() else []


async def _file_write_all(receipts: list[dict]) -> None:
    import aiofiles
    async with aiofiles.open(RECEIPTS_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(receipts, ensure_ascii=False, indent=2, default=str))


# ── 공개 인터페이스 ───────────────────────────────────────────────────────────
async def list_receipts() -> list[dict]:
    if USE_NEON_DB:
        pool = await _get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id,store_name,date,total_amount,items,raw_ocr,"
                "image_filename,category,memo,created_at,updated_at "
                "FROM receipts ORDER BY created_at DESC"
            )
        return [_row_to_dict(r) for r in rows]
    if USE_VERCEL_KV:
        data = await _redis.get(_KV_KEY)
        return json.loads(data) if data else []
    return await _file_read_all()


async def get_receipt(receipt_id: str) -> dict | None:
    if USE_NEON_DB:
        pool = await _get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id,store_name,date,total_amount,items,raw_ocr,"
                "image_filename,category,memo,created_at,updated_at "
                "FROM receipts WHERE id = $1",
                receipt_id,
            )
        return _row_to_dict(row) if row else None
    if USE_VERCEL_KV:
        receipts = json.loads(await _redis.get(_KV_KEY) or "[]")
        return next((r for r in receipts if r["id"] == receipt_id), None)
    receipts = await _file_read_all()
    return next((r for r in receipts if r["id"] == receipt_id), None)


async def get_receipt_image(receipt_id: str) -> tuple[bytes, str] | None:
    """이미지 바이트와 MIME 타입 반환 (Neon 전용)."""
    if not USE_NEON_DB:
        return None
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT image_data, image_mime FROM receipts WHERE id = $1",
            receipt_id,
        )
    if not row or not row["image_data"]:
        return None
    return bytes(row["image_data"]), row["image_mime"] or "image/jpeg"


async def create_receipt(
    receipt: Receipt,
    image_data: bytes | None = None,
    image_mime: str = "image/jpeg",
) -> dict:
    data = receipt.model_dump()
    if USE_NEON_DB:
        pool = await _get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO receipts
                    (id,store_name,date,total_amount,items,raw_ocr,
                     image_filename,image_data,image_mime,category,memo,created_at,updated_at)
                VALUES ($1,$2,$3,$4,$5::jsonb,$6,$7,$8,$9,$10,$11,$12,$13)
            """,
                data["id"], data["store_name"], data["date"], data["total_amount"],
                json.dumps(data["items"], default=str),
                data["raw_ocr"], data["image_filename"],
                image_data, image_mime,
                data["category"], data["memo"],
                data["created_at"], data["updated_at"],
            )
        return data
    if USE_VERCEL_KV:
        receipts = json.loads(await _redis.get(_KV_KEY) or "[]")
        receipts.append(data)
        await _redis.set(_KV_KEY, json.dumps(receipts, ensure_ascii=False, default=str))
        return data
    receipts = await _file_read_all()
    receipts.append(data)
    await _file_write_all(receipts)
    return data


async def update_receipt(receipt_id: str, updates: dict) -> dict | None:
    if USE_NEON_DB:
        updates["updated_at"] = datetime.now()
        set_clause = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
        values = list(updates.values())
        pool = await _get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"UPDATE receipts SET {set_clause} WHERE id = $1 "
                "RETURNING id,store_name,date,total_amount,items,raw_ocr,"
                "image_filename,category,memo,created_at,updated_at",
                receipt_id, *values,
            )
        return _row_to_dict(row) if row else None
    if USE_VERCEL_KV:
        receipts = json.loads(await _redis.get(_KV_KEY) or "[]")
        for i, r in enumerate(receipts):
            if r["id"] == receipt_id:
                receipts[i].update(updates)
                receipts[i]["updated_at"] = datetime.now().isoformat()
                await _redis.set(_KV_KEY, json.dumps(receipts, ensure_ascii=False, default=str))
                return receipts[i]
        return None
    receipts = await _file_read_all()
    for i, r in enumerate(receipts):
        if r["id"] == receipt_id:
            receipts[i].update(updates)
            receipts[i]["updated_at"] = datetime.now().isoformat()
            await _file_write_all(receipts)
            return receipts[i]
    return None


async def delete_receipt(receipt_id: str) -> bool:
    if USE_NEON_DB:
        pool = await _get_pool()
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM receipts WHERE id = $1", receipt_id)
        return result == "DELETE 1"
    if USE_VERCEL_KV:
        receipts = json.loads(await _redis.get(_KV_KEY) or "[]")
        filtered = [r for r in receipts if r["id"] != receipt_id]
        if len(filtered) == len(receipts):
            return False
        await _redis.set(_KV_KEY, json.dumps(filtered, ensure_ascii=False, default=str))
        return True
    receipts = await _file_read_all()
    filtered = [r for r in receipts if r["id"] != receipt_id]
    if len(filtered) == len(receipts):
        return False
    await _file_write_all(filtered)
    return True
