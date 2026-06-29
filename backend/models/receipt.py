from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    name: str
    price: int
    quantity: int = 1


class ReceiptCreate(BaseModel):
    store_name: str = ""
    date: str = ""
    total_amount: int = 0
    items: list[ReceiptItem] = []
    category: str = "기타"
    memo: str = ""


class Receipt(ReceiptCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    image_filename: str = ""
    raw_ocr: str = ""


class ReceiptUpdate(BaseModel):
    store_name: Optional[str] = None
    date: Optional[str] = None
    total_amount: Optional[int] = None
    items: Optional[list[ReceiptItem]] = None
    category: Optional[str] = None
    memo: Optional[str] = None
