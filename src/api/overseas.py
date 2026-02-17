from src.api.base import BaseAPI
from src.config_loader import get_account_no, get_account_code

class OverseasAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.cano = get_account_no()
        self.acnt_prdt_cd = get_account_code()

    def get_balance_present(self, nation="000"):
        """Overseas Stock Present Balance Inquiry (CTRP6504R)"""
        path = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        tr_id = "CTRP6504R"
        
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "WCRC_FRCR_DVSN_CD": "02",
            "NATN_CD": nation,
            "TR_MKET_CD": "00",
            "INQR_DVSN_CD": "00"
        }
        
        return self.call_api(path, params=params, tr_id=tr_id)

    def get_balance_realtime(self, exchange="NASD", currency="USD"):
        """Overseas Stock Realtime Balance Inquiry (TTZC3013R)"""
        path = "/uapi/overseas-stock/v1/trading/inquire-balance"
        tr_id = "TTZC3013R"
        
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange,
            "TR_CRC_CD": currency,
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }
        
        return self.call_api(path, params=params, tr_id=tr_id)

    def order(self, symbol, quantity, price, side="BUY", exchange="NASD"):
        """
        Overseas Stock Order (USA)
        side: "BUY" or "SELL"
        """
        path = "/uapi/overseas-stock/v1/trading/order"
        
        # TR_ID for USA (NASD, NYSE, AMEX)
        # Buy: JTTT1002U, Sell: JTTT1006U (Real)
        # Check if VTS (Virtual)? Config should handle base URL, but TR_ID differs for VTS.
        # Assuming Real for now based on previous context.
        tr_id = "JTTT1002U" if side.upper() == "BUY" else "JTTT1006U"
        
        data = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange,
            "PDNO": symbol,
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price),
            "ORD_SVR_DVSN_CD": "0", # 0: False(Default)
            "ORD_DVSN": "00" # 00: Limit, 32: Market (for Overseas, usually 00)
        }
        
        return self.call_api(path, data=data, method="POST", tr_id=tr_id)
