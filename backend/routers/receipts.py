from __future__ import annotations

import os
import uuid

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import IMAGES_DIR
from backend.models.receipt import Receipt, ReceiptUpdate
from backend.services import ocr_service, storage_service

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/upload", status_code=201)
async def upload_receipt(file: UploadFile = File(...)):
    """영수증 이미지 업로드 → OCR → 저장."""
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(400, "지원하지 않는 파일 형식입니다. (jpg, png, webp 허용)")

    image_bytes = await file.read()

    # 이미지 저장
    ext = os.path.splitext(file.filename or "receipt.jpg")[1] or ".jpg"
    image_filename = f"receipt_{uuid.uuid4().hex}{ext}"
    async with aiofiles.open(os.path.join(IMAGES_DIR, image_filename), "wb") as f:
        await f.write(image_bytes)

    # OCR 호출
    try:
        ocr_result = await ocr_service.parse_receipt(image_bytes, file.filename or "receipt.jpg")
    except Exception as e:
        raise HTTPException(502, f"OCR 처리 중 오류가 발생했습니다: {e}")

    extracted = ocr_service.extract_receipt_info(ocr_result)

    receipt = Receipt(image_filename=image_filename, **extracted)
    saved = await storage_service.create_receipt(receipt)
    return saved


@router.get("")
async def list_receipts():
    """전체 지출 목록 조회."""
    return await storage_service.list_receipts()


@router.get("/{receipt_id}")
async def get_receipt(receipt_id: str):
    """단건 조회."""
    receipt = await storage_service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
    return receipt


@router.put("/{receipt_id}")
async def update_receipt(receipt_id: str, body: ReceiptUpdate):
    """지출 정보 수정."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "수정할 항목이 없습니다.")
    updated = await storage_service.update_receipt(receipt_id, updates)
    if not updated:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
    return updated


@router.delete("/{receipt_id}", status_code=204)
async def delete_receipt(receipt_id: str):
    """지출 삭제."""
    deleted = await storage_service.delete_receipt(receipt_id)
    if not deleted:
        raise HTTPException(404, "영수증을 찾을 수 없습니다.")
