"""
OCR Service using Google Gemini Vision API (google-genai SDK).
Extracts structured asset and trade data from brokerage app screenshots.
"""

import json
import re
import io

from src.config_loader import load_config


import time
import logging

logger = logging.getLogger(__name__)

# 사용 가능한 모델 (할당량 확인 기준)
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]


def _call_gemini(image_bytes: bytes, prompt: str) -> dict:
    """Call Gemini Vision API and parse JSON response. Retries on rate limit."""
    try:
        from google import genai
    except ImportError:
        raise ImportError(
            "google-genai 패키지가 설치되지 않았습니다. "
            "pip install google-genai 로 설치하세요."
        )

    config = load_config()
    api_key = config.get("gemini", {}).get("api_key")
    if not api_key:
        raise ValueError("Gemini API key not found in config. Add 'gemini.api_key' to secrets.yaml")

    client = genai.Client(api_key=api_key)

    # Detect mime type
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes))
    fmt = (img.format or "PNG").lower()
    mime = f"image/{fmt}"

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):  # 최대 2회 시도
            try:
                logger.info(f"Calling Gemini model={model_name}, attempt={attempt+1}")
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        prompt,
                        genai.types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    ],
                    config=genai.types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=2048,
                    ),
                )

                text = response.text.strip()

                # Strip markdown code fences if present
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)

                return json.loads(text)

            except Exception as e:
                last_error = e
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"Rate limited on {model_name}, waiting 30s...")
                    time.sleep(30)
                    continue
                else:
                    raise

    raise last_error or Exception("모든 모델에서 할당량이 초과되었습니다. 잠시 후 다시 시도하세요.")


ASSET_PROMPT = """
이 이미지는 한국 증권사 앱의 보유 자산 화면 스크린샷입니다.
이미지에서 보유 자산 정보를 추출하여 아래 JSON 형식으로 반환하세요.

반환 형식:
{
  "assets": [
    {
      "name": "종목명 (예: 삼성전자)",
      "symbol": "종목코드 (예: 005930, AAPL) - 없으면 null",
      "asset_type": "자산 유형 (stock/etf/fund/crypto/bond/cash 중 하나)",
      "quantity": 보유수량 (숫자),
      "buy_price": 평균매입가 (숫자, 원화),
      "current_price": 현재가 (숫자, 원화),
      "currency": "통화 (KRW/USD/JPY 등)",
      "brokerage": "증권사명 (예: 한국투자증권, 삼성증권) - 모르면 null"
    }
  ],
  "confidence": "high/medium/low",
  "notes": "인식 과정에서 특이사항이나 불확실한 부분"
}

주의사항:
- 숫자에서 쉼표(,)와 단위(원, 주, 좌)를 제거하고 순수 숫자만 반환
- 인식이 불확실한 필드는 null로 표시
- 이미지에 자산 정보가 없으면 assets를 빈 배열로 반환
- JSON만 반환하고 다른 텍스트는 포함하지 마세요
"""

TRADE_PROMPT = """
이 이미지는 한국 증권사 앱의 거래 내역 화면 스크린샷입니다.
이미지에서 거래 내역을 추출하여 아래 JSON 형식으로 반환하세요.

반환 형식:
{
  "trades": [
    {
      "trade_date": "거래일자 (YYYY-MM-DD 형식)",
      "name": "종목명",
      "symbol": "종목코드 - 없으면 null",
      "trade_type": "매수/매도 (buy/sell)",
      "quantity": 거래수량 (숫자),
      "price": 거래단가 (숫자, 원화),
      "total_amount": 거래금액 (숫자, 원화),
      "fee": 수수료 (숫자) - 없으면 0,
      "currency": "통화 (KRW/USD 등)",
      "brokerage": "증권사명 - 모르면 null"
    }
  ],
  "confidence": "high/medium/low",
  "notes": "인식 과정에서 특이사항이나 불확실한 부분"
}

주의사항:
- 숫자에서 쉼표(,)와 단위(원, 주)를 제거하고 순수 숫자만 반환
- 날짜 형식을 YYYY-MM-DD로 통일
- 인식이 불확실한 필드는 null로 표시
- 이미지에 거래 내역이 없으면 trades를 빈 배열로 반환
- JSON만 반환하고 다른 텍스트는 포함하지 마세요
"""


def extract_assets_from_screenshot(image_bytes: bytes) -> dict:
    """
    Extract asset holdings from a brokerage app screenshot.
    Returns structured dict with 'assets' list.
    """
    try:
        result = _call_gemini(image_bytes, ASSET_PROMPT)
        return {"success": True, "data": result}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON 파싱 실패: {str(e)}", "data": {"assets": []}}
    except Exception as e:
        return {"success": False, "error": str(e), "data": {"assets": []}}


def extract_trades_from_screenshot(image_bytes: bytes) -> dict:
    """
    Extract trade history from a brokerage app screenshot.
    Returns structured dict with 'trades' list.
    """
    try:
        result = _call_gemini(image_bytes, TRADE_PROMPT)
        return {"success": True, "data": result}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON 파싱 실패: {str(e)}", "data": {"trades": []}}
    except Exception as e:
        return {"success": False, "error": str(e), "data": {"trades": []}}
