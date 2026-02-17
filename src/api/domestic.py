from src.api.base import BaseAPI
from src.config_loader import get_account_no, get_account_code

class DomesticAPI(BaseAPI):
    def __init__(self):
        super().__init__()
        self.cano = get_account_no()
        self.acnt_prdt_cd = get_account_code()

    def get_balance(self):
        """Domestic Stock Balance Inquiry (TTTC8434R)"""
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        tr_id = "TTTC8434R"
        
        # Check if virtual trading? (Base URL handles it but TR_ID might differ)
        # For now assume real trading
        
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        return self.call_api(path, params=params, tr_id=tr_id)

    def get_current_price(self, code):
        """Domestic Stock Current Price Inquiry (FHKST01010100)"""
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        tr_id = "FHKST01010100"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": code
        }
        
        return self.call_api(path, params=params, tr_id=tr_id)

    def order_cash(self, code, quantity, price, side="BUY"):
        """
        Domestic Stock Cash Order
        side: "BUY" or "SELL"
        price: '0' for Market Price (requires different order code), otherwise Limit Price
        """
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        
        # Determine TR_ID
        # Buy: TTTC0802U, Sell: TTTC0801U
        tr_id = "TTTC0802U" if side.upper() == "BUY" else "TTTC0801U"
        
        data = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "PDNO": code,
            "ORD_DVSN": "00", # 00: Limit, 01: Market
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
        }
        
        return self.call_api(path, data=data, method="POST", tr_id=tr_id)
