from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.logic import executor, AssetType

router = APIRouter(prefix="/api/trade", tags=["trade"])

class OrderRequest(BaseModel):
    asset_type: str # "DOMESTIC" or "OVERSEAS"
    symbol: str
    side: str # "BUY" or "SELL"
    quantity: float
    price: float
    exchange: str = "NASD" # For overseas only

@router.post("/order")
async def place_order(req: OrderRequest):
    """
    Manual order placement endpoint.
    """
    atype = AssetType.STOCK_DOMESTIC if req.asset_type == "DOMESTIC" else AssetType.STOCK_OVERSEAS
    
    success, msg = executor.execute_order(
        asset_type=atype,
        symbol=req.symbol,
        side=req.side,
        quantity=req.quantity,
        price=req.price,
        exchange=req.exchange
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Order Failed: {msg}")
        
    return {"status": "success", "message": msg}
