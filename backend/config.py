import os
from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY: str = os.getenv("UPSTAGE_API_KEY", "")

# Vercel KV (Upstash Redis) — 설정 시 파일 스토리지 대신 사용
KV_REST_API_URL: str = os.getenv("KV_REST_API_URL", "")
KV_REST_API_TOKEN: str = os.getenv("KV_REST_API_TOKEN", "")
USE_VERCEL_KV: bool = bool(KV_REST_API_URL)

# Vercel Blob — 설정 시 로컬 이미지 저장 대신 사용
BLOB_READ_WRITE_TOKEN: str = os.getenv("BLOB_READ_WRITE_TOKEN", "")
USE_VERCEL_BLOB: bool = bool(BLOB_READ_WRITE_TOKEN)

# 로컬 개발용 경로
_BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(_BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
RECEIPTS_FILE = os.path.join(DATA_DIR, "receipts.json")

if not USE_VERCEL_BLOB:
    os.makedirs(IMAGES_DIR, exist_ok=True)
