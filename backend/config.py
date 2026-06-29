import os
from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY: str = os.getenv("UPSTAGE_API_KEY", "")

# backend/ 기준 경로
_BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(_BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
RECEIPTS_FILE = os.path.join(DATA_DIR, "receipts.json")

# 디렉토리 보장
os.makedirs(IMAGES_DIR, exist_ok=True)
