from __future__ import annotations

import mimetypes
import os
import uuid

import aiofiles
import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import (
    IMAGES_DIR, USE_VERCEL_BLOB, BLOB_READ_WRITE_TOKEN,
)
from backend.models.receipt import Receipt, ReceiptUpdate
from backend.services import ocr_service, storage_service

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
_BLOB_API = "https://blob.vercel-storage.com"


async def _save_image(image_bytes: bytes, original_filename: str) -> str:
    """이미지를 저장하고 식별자(로컬 파일명 또는 Blob URL)를 반환한다."""
    ext = os.path.splitext(original_filename)[1] or ".jpg"
    unique_name = f"receipt_{uuid.uuid4().hex}{ext}"
    mime = mimetypes.guess_type(original_filename)[0] or "image/jpeg"

    if USE_VERCEL_BLOB:
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

    # 로컬 개발: 파일시스템에 저장
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

    image_identifier = await _save_image(image_bytes, filename)

    try:
        ocr_result = await ocr_service.parse_receipt(image_bytes, filename)
    except Exception as e:
        raise HTTPException(502, f"OCR 처리 중 오류가 발생했습니다: {e}")

    extracted = ocr_service.extract_receipt_info(ocr_result)
    receipt = Receipt(image_filename=image_identifier, **extracted)
    saved = await storage_service.create_receipt(receipt)
    return saved


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
