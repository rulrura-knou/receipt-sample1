import os
from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY: str = os.getenv("UPSTAGE_API_KEY", "")

# Neon PostgreSQL — Vercel 연동 시 POSTGRES_URL 자동 주입, 직접 설정 시 DATABASE_URL
DATABASE_URL: str = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL", "")
USE_NEON_DB: bool = bool(DATABASE_URL)

# Vercel KV (Upstash Redis) — Neon 미사용 시 폴백
KV_REST_API_URL: str = os.getenv("KV_REST_API_URL", "")
KV_REST_API_TOKEN: str = os.getenv("KV_REST_API_TOKEN", "")
USE_VERCEL_KV: bool = bool(KV_REST_API_URL) and not USE_NEON_DB

# Vercel Blob — 이미지 저장
BLOB_READ_WRITE_TOKEN: str = os.getenv("BLOB_READ_WRITE_TOKEN", "")
USE_VERCEL_BLOB: bool = bool(BLOB_READ_WRITE_TOKEN)

# 로컬 개발용 경로
_BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(_BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
RECEIPTS_FILE = os.path.join(DATA_DIR, "receipts.json")

if not USE_VERCEL_BLOB:
    os.makedirs(IMAGES_DIR, exist_ok=True)
