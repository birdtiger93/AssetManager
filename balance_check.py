import requests
import json
import pandas as pd
from datetime import datetime
import sys
import io
import os
import time

# 윈도우 터미널 한글 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# --- 한국투자증권 API 설정 정보 ---
APP_KEY = "PSKathJKCFoaHDh6gVITH5gC3sRhmGILFZXa"
APP_SECRET = "mvn08ZOmNA6LzirPE8VrcK1UyQ95I15LkbnRtSF13BJEV9uP6+mJml4C9xCGkn3OM+4jFbuweJ2K8ypFcTRofWq3Rqo2oB/oyn2M4rvjd8cduSyDfaEOF7r/043/Jl8H8g2CCNegoqahJZfZ9WFMkhOJXhbQOrP2Np7BYMujOOd5enlUln4="
CANO = "46865039"           # 계좌번호 8자리
ACNT_PRDT_CD = "01"         # 계좌상품코드
URL_BASE = "https://openapi.koreainvestment.com:9443"

TOKEN_FILE = "token.json"

def get_access_token():
    """접근 토큰(Access Token) 발급 및 캐싱"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
            if time.time() - token_data.get("issued_at", 0) < 23 * 3600:
                return token_data.get("access_token")

    path = "/oauth2/tokenP"
    url = f"{URL_BASE}{path}"
    headers = {"content-type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    if res.status_code == 200:
        token_info = res.json()
        access_token = token_info.get("access_token")
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"access_token": access_token, "issued_at": time.time()}, f)
        return access_token
    else:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("access_token")
        return None

def get_overseas_balance_realtime(token, exchange="NASD", currency="USD"):
    """해외주식 실시간 잔고 조회 (TR: TTZC3013R)"""
    path = "/uapi/overseas-stock/v1/trading/inquire-balance"
    url = f"{URL_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "TTZC3013R"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "OVRS_EXCG_CD": exchange,
        "TR_CRC_CD": currency,
        "CTX_AREA_FK200": "",
        "CTX_AREA_NK200": ""
    }
    res = requests.get(url, headers=headers, params=params)
    return res.json() if res.status_code == 200 else None

def get_overseas_balance_present(token, nation="000"):
    """해외주식 체결기준 현재잔고 조회 (TR: CTRP6504R)"""
    path = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
    url = f"{URL_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "CTRP6504R"
    }
    params = {
        "CANO": CANO, "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "WCRC_FRCR_DVSN_CD": "02", "NATN_CD": nation,
        "TR_MKET_CD": "00", "INQR_DVSN_CD": "00"
    }
    res = requests.get(url, headers=headers, params=params)
    return res.json() if res.status_code == 200 else None

def main():
    print("해외 주식 잔고 조회를 시작합니다...")
    token = get_access_token()
    if not token:
        print("토큰 획득 실패")
        return

    # 1. 요약 정보 (CTRP6504R)
    present_res = get_overseas_balance_present(token)

    
    print("\n" + "="*80)
    print(f" [해외주식 계좌 요약] - 조회시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    if present_res and present_res.get("rt_cd") == "0":
        summary = present_res.get("output3", {})
        
        # 외화(USD) 기준 요약
        print(f" [외화(USD) 기준 요약]")
        print(f" - 총 매입 금액: ${float(summary.get('pchs_amt_smtl', 0)):,.2f}")
        print(f" - 총 평가 금액: ${float(summary.get('evlu_amt_smtl', 0)):,.2f}")
        print(f" - 총 평가 손익: ${float(summary.get('evlu_pfls_amt_smtl', 0)):,.2f}")
        
        # 원화 환산 기준 요약
        print(f"\n [원화 환산 요약]")
        print(f" - 총 매입 금액: {float(summary.get('pchs_amt_smtl_amt', 0)):,.0f} KRW")
        print(f" - 총 평가 금액: {float(summary.get('evlu_amt_smtl_amt', 0)):,.0f} KRW")
        print(f" - 총 평가 손익: {float(summary.get('tot_evlu_pfls_amt', 0)):,.0f} KRW")
        
        # 수익률 및 자산
        raw_rt = float(summary.get('evlu_erng_rt1', 0))
        display_rt = 0.0 if raw_rt == -1000.0 else raw_rt
        print(f"\n - 전체 수익률: {display_rt:,.2f} %")
        print(f" - 외화 예수금: {float(summary.get('tot_frcr_cblc_smtl', 0)):,.0f} KRW (원화환산)")

        currency_list = present_res.get("output2", [])
        if currency_list:
            print("\n [통화별 예수금 상세]")
            for curr in currency_list:
                print(f" * {curr.get('crcy_cd_name')} ({curr.get('crcy_cd')}): {float(curr.get('frcr_dncl_amt_2', 0)):,.2f} (환율: {float(curr.get('frst_bltn_exrt', 0)):,.2f})")

    # 2. 보유 종목 리스트 (TTZC3013R로 여러 거래소 확인)
    print("\n" + "-"*80)
    print(" [보유 종목 상세 리스트]")
    print("-"*80)

    def clean_profit_rate(val):
        """수익률이 -1000% 등으로 오는 경우 예외 처리"""
        try:
            f_val = float(val)
            if f_val <= -1000.0 or f_val == -100.0: # 보통 -1000은 데이터 없음/오류 의미
                return 0.0
            return f_val
        except (ValueError, TypeError):
            return 0.0

    all_holdings = []
    # 1. 먼저 상세 잔고(CTRP6504R)의 output1을 기반으로 리스트 생성 (더 정확한 정보 포함)
    if present_res and present_res.get("rt_cd") == "0":
        for item in present_res.get("output1", []):
            qty = float(item.get("ccld_qty_smtl1", 0))
            if qty > 0:
                all_holdings.append({
                    "거래소": item.get("tr_mket_name", ""),
                    "종목코드": item.get("pdno"),
                    "종목명": item.get("prdt_name"),
                    "보유수량": qty,
                    "매입단가": float(item.get("avg_unpr3", 0)),
                    "현재가": float(item.get("ovrs_now_pric1", 0)),
                    "평가손익": float(item.get("evlu_pfls_amt2", 0)),
                    "수익률(%)": clean_profit_rate(item.get("evlu_pfls_rt1", 0))
                })

    # 2. 만약 상세 잔고에서 가져온게 없으면 기존 방식(거래소별 실시간 조회) 시도
    if not all_holdings:
        for exch in ["NASD", "NYSE", "AMEX"]:
            realtime_res = get_overseas_balance_realtime(token, exchange=exch)
            if realtime_res and realtime_res.get("rt_cd") == "0":
                for item in realtime_res.get("output1", []):
                    qty = float(item.get("hldg_qty", 0))
                    if qty > 0:
                        all_holdings.append({
                            "거래소": exch,
                            "종목코드": item.get("ovrs_pdno"),
                            "종목명": item.get("ovrs_item_name"),
                            "보유수량": qty,
                            "매입단가": float(item.get("pchs_avg_pric", 0)),
                            "현재가": float(item.get("now_pric1", 0)),
                            "평가손익": float(item.get("evlu_pfls_amt", 0)),
                            "수익률(%)": clean_profit_rate(item.get("evlu_pfls_rt", 0))
                        })
    
    if all_holdings:
        df = pd.DataFrame(all_holdings)
        pd.options.display.float_format = '{:,.2f}'.format
        # 컬럼 순서 조정
        cols = ["거래소", "종목코드", "종목명", "보유수량", "매입단가", "현재가", "평가손익", "수익률(%)"]
        print(df[cols].to_string(index=False))
    else:
        print("보유 중인 해외 종목을 찾을 수 없습니다.")

    # 디버그 파일 삭제 (선택 사항)
    if os.path.exists("debug_present_res.json"):
        os.remove("debug_present_res.json")


    print("="*80 + "\n")

if __name__ == "__main__":
    main()