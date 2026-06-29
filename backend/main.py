from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import IMAGES_DIR
from backend.routers import receipts

app = FastAPI(
    title="영수증 지출관리 API",
    version="0.1.0",
    description="영수증 OCR 기반 지출 관리 백엔드",
)

# React 개발서버(3000, 5173) 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(receipts.router)

# 업로드된 영수증 이미지를 /static/images/{filename} 으로 제공
app.mount("/static/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/")
def root():
    return {"status": "ok", "message": "영수증 지출관리 API"}
