from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import IMAGES_DIR, USE_VERCEL_BLOB
from backend.routers import receipts

app = FastAPI(
    title="영수증 지출관리 API",
    version="0.1.0",
    description="영수증 OCR 기반 지출 관리 백엔드",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(receipts.router)

# 로컬 개발 전용: Vercel Blob 사용 시 이미지는 CDN에서 직접 서빙
if not USE_VERCEL_BLOB:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/")
def root():
    return {"status": "ok", "message": "영수증 지출관리 API"}
