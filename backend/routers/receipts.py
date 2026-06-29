from __future__ import annotations

import mimetypes
import os
import uuid

import aiofiles
import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from backend.config import (
    IMAGES_DIR, USE_VERCEL_BLOB, BLOB_READ_WRITE_TOKEN, USE_NEON_DB,
)
from backend.models.receipt import Receipt, ReceiptUpdate
from backend.services import ocr_service, storage_service

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_BLOB_API = "https://blob.vercel-storage.com"


async def _upload_to_blob(image_bytes: bytes, filename: str, mime: str) -> str:
    unique_name = f"receipt_{uuid.uuid4().hex}{os.path.splitext(filename)[1] or '.jpg'}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.put(
            f"{_BLOB_API}/{unique_name}",
            content=image_bytes,
            headers={
                "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                "x-api-version": "7",
                "Content-Type": mime,
            },
        )
        resp.raise_for_status()
        return resp.json()["url"]


async def _save_local(image_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1] or ".jpg"
    unique_name = f"receipt_{uuid.uuid4().hex}{ext}"
    path = os.path.join(IMAGES_DIR, unique_name)
    async with aiofiles.open(path, "wb") as f:
        await f.write(image_bytes)
    return unique_name


@router.post("/upload", status_code=201)
async def upload_receipt(file: UploadFile = File(...)):
    """영수증 이미지 업로드 → OCR → 저장."""
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(400, "지원하지 않는 파일 형식입니다. (jpg, png, webp 허용)")

    image_bytes = await file.read()
    filename = file.filename or "receipt.jpg"
    mime = mimetypes.guess_type(filename)[0] or "image/jpeg"

    try:
        ocr_result = await ocr_service.parse_receipt(image_bytes, filename)
    except Exception as e:
        raise HTTPException(502, f"OCR 처리 중 오류가 발생했습니다: {e}")

    extracted = ocr_service.extract_receipt_info(ocr_result)
    receipt = Receipt(**extracted)

    # 이미지 저장 전략
    if USE_VERCEL_BLOB:
        receipt.image_filename = await _upload_to_blob(image_bytes, filename, mime)
        saved = await storage_service.create_receipt(receipt)
    elif USE_NEON_DB:
        # Neon DB에 BYTEA로 저장, API 엔드포인트로 서빙
        receipt.image_filename = f"/api/receipts/{receipt.id}/image"
        saved = await storage_service.create_receipt(receipt, image_data=image_bytes, image_mime=mime)
    else:
        # 로컬 개발: 파일시스템
        image_filename = await _save_local(image_bytes, filename)
        receipt.image_filename = image_filename
        saved = await storage_service.create_receipt(receipt)

    return saved


@router.get("/{receipt_id}/image")
async def get_receipt_image(receipt_id: str):
    """Neon DB에 저장된 이미지를 바이너리로 반환."""
    result = await storage_service.get_receipt_image(receipt_id)
    if not result:
        raise HTTPException(404, "이미지를 찾을 수 없습니다.")
    image_bytes, mime = result
    return Response(content=image_bytes, media_type=mime)


@router.get("")
async def list_receipts():
    return await storage_service.list_receipts()


@router.get("/{receipt_id}")
async def get_receipt(receipt_id: str):
    receipt = await storage_service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
    return receipt


@router.put("/{receipt_id}")
async def update_receipt(receipt_id: str, body: ReceiptUpdate):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "수정할 항목이 없습니다.")
    updated = await storage_service.update_receipt(receipt_id, updates)
    if not updated:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
    return updated


@router.delete("/{receipt_id}", status_code=204)
async def delete_receipt(receipt_id: str):
    deleted = await storage_service.delete_receipt(receipt_id)
    if not deleted:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
