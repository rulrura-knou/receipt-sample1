from __future__ import annotations

import mimetypes
import re

import httpx

from backend.config import UPSTAGE_API_KEY

_UPSTAGE_URL = "https://api.upstage.ai/v1/document-ai/document-parse"


async def parse_receipt(image_bytes: bytes, filename: str) -> dict:
    """Upstage Document Parse API 호출 후 원본 응답 반환."""
    mime_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            _UPSTAGE_URL,
            headers={"Authorization": f"Bearer {UPSTAGE_API_KEY}"},
            files={"document": (filename, image_bytes, mime_type)},
            data={"output_formats": '["markdown", "text"]'},
        )
        response.raise_for_status()
        return response.json()


def _parse_amount(text: str) -> int:
    """숫자와 쉼표만 남겨 정수로 변환. 실패 시 0 반환."""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def extract_receipt_info(ocr_result: dict) -> dict:
    """OCR 응답에서 영수증 핵심 정보를 추출한다."""
    markdown: str = ocr_result.get("content", {}).get("markdown", "")

    info: dict = {
        "store_name": "",
        "date": "",
        "total_amount": 0,
        "items": [],
        "raw_ocr": markdown,
    }

    lines = [ln.strip() for ln in markdown.splitlines()]

    # 상호명: 첫 번째 의미 있는 텍스트 줄
    for line in lines:
        cleaned = re.sub(r"^#+\s*", "", line).strip()
        if cleaned and len(cleaned) > 1:
            info["store_name"] = cleaned
            break

    for line in lines:
        # 날짜: YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
        if not info["date"]:
            m = re.search(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", line)
            if m:
                y, mo, d = m.groups()
                info["date"] = f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

    # ── 합계 금액 추출 ─────────────────────────────────────────
    # 금액 패턴: 쉼표 뒤 공백 허용(6, 818 대응) + 4자리 이상 연속 숫자
    _AMT = r"(\d{1,3}(?:,\s*\d{3})+|\d{4,})"

    # 1단계: 합계 키워드가 같은 줄/셀에 있는 표준 형식
    #        합.{0,10}계 로 분리 셀(| 합 | 계 |)도 처리
    #        .{0,80}? 로 colspan="2" 같은 HTML 속성 숫자 건너뜀
    m = re.search(
        r"(?:합.{0,10}계|총\s*액|총\s*계|결제\s*금액|받을\s*금액|TOTAL)"
        r".{0,80}?" + _AMT,
        markdown, re.IGNORECASE | re.DOTALL,
    )
    if m:
        info["total_amount"] = _parse_amount(m.group(1))

    # 2단계: 합계 셀이 OCR 오인식으로 손상된 경우 → 금액 + 부가세 합산
    #        예) '7,500' → '' 500' (7, 가 따옴표로 오인식)
    #        금.{0,5}액 으로 분리 셀(| 금 | 액 |)도 처리
    if info["total_amount"] == 0:
        sub_m = re.search(
            r"(?:금.{0,5}액|소\s*계|과세\s*금액).{0,40}?" + _AMT,
            markdown, re.IGNORECASE | re.DOTALL,
        )
        tax_m = re.search(
            r"부.{0,5}가.{0,5}세.{0,40}?(\d{1,3}(?:,\s*\d{3})+|\d{3,})",
            markdown, re.IGNORECASE | re.DOTALL,
        )
        if sub_m and tax_m:
            subtotal = _parse_amount(sub_m.group(1))
            tax = _parse_amount(tax_m.group(1))
            if subtotal > 0 and tax > 0:
                info["total_amount"] = subtotal + tax

    return info
