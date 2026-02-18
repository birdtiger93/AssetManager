"""
OCR Router - Image upload and data extraction endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.ocr_service import extract_assets_from_screenshot, extract_trades_from_screenshot

router = APIRouter(prefix="/api/ocr", tags=["ocr"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
MAX_SIZE_MB = 10


@router.post("/extract-assets")
async def extract_assets(file: UploadFile = File(...)):
    """
    Upload a brokerage app screenshot and extract asset holdings.
    Returns structured JSON with asset data for user review.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: JPEG, PNG, WebP"
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다. 최대 {MAX_SIZE_MB}MB까지 허용됩니다."
        )

    result = extract_assets_from_screenshot(image_bytes)

    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=f"이미지 분석 실패: {result.get('error', '알 수 없는 오류')}"
        )

    return result["data"]


@router.post("/extract-trades")
async def extract_trades(file: UploadFile = File(...)):
    """
    Upload a brokerage app screenshot and extract trade history.
    Returns structured JSON with trade data for user review.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: JPEG, PNG, WebP"
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 너무 큽니다. 최대 {MAX_SIZE_MB}MB까지 허용됩니다."
        )

    result = extract_trades_from_screenshot(image_bytes)

    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=f"이미지 분석 실패: {result.get('error', '알 수 없는 오류')}"
        )

    return result["data"]
