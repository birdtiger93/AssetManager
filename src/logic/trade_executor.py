from datetime import datetime
from src.database.engine import SessionLocal
from src.database.models import TradeLog, AssetType
from src.api.domestic import DomesticAPI
from src.api.overseas import OverseasAPI

class TradeExecutor:
    def __init__(self):
        self.dom_api = DomesticAPI()
        self.ov_api = OverseasAPI()

    def execute_order(self, asset_type: AssetType, symbol: str, side: str, quantity: float, price: float, exchange="NASD"):
        """
        Executes an order and logs it.
        side: "BUY" or "SELL"
        """
        print(f"[ORDER] Processing {side} {symbol} ({quantity} @ {price})...")
        
        res = None
        executed = False
        msg = ""

        try:
            if asset_type == AssetType.STOCK_DOMESTIC:
                res = self.dom_api.order_cash(symbol, quantity, price, side)
            elif asset_type == AssetType.STOCK_OVERSEAS:
                res = self.ov_api.order(symbol, quantity, price, side, exchange)
            
            if res and res.get("rt_cd") == "0":
                executed = True
                msg = res.get("msg1", "Success")
                order_no = res.get("output", {}).get("ODNO") # Order Number
                print(f"[ORDER] Success! Order No: {order_no}")
            else:
                msg = res.get("msg1") if res else "Unknown Error"
                print(f"[ORDER] Failed: {msg}")

        except Exception as e:
            msg = str(e)
            print(f"[ORDER] Exception: {e}")

        # Log to DB
        self._log_trade(asset_type, symbol, side, quantity, price, msg)
        return executed, msg

    def _log_trade(self, asset_type, symbol, side, quantity, price, msg):
        db = SessionLocal()
        try:
            log = TradeLog(
                timestamp=datetime.utcnow(),
                asset_type=asset_type,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                result_msg=msg
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"[ERROR] Failed to log trade: {e}")
        finally:
            db.close()

# Global Instance
executor = TradeExecutor()
