from datetime import datetime
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd

from src.database.engine import get_db
from src.database.models import ManualAsset
from src.api.overseas import OverseasAPI
from src.api.domestic import DomesticAPI

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

def clean_profit_rate(val):
    try:
        f_val = float(val)
        if f_val <= -1000.0 or f_val == -100.0:
            return 0.0
        return f_val
    except:
        return 0.0

@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns the aggregated portfolio summary using Integrated Account Balance (CTRP6548R) and Manual Assets.
    """
    
    # 1. Fetch Integrated Balance (CTRP6548R)
    dom_api = DomesticAPI()
    integ_res = dom_api.get_account_balance()
    
    asset_classification = {
        "domestic_stock": {"amount": 0, "profit": 0, "percent": 0},
        "overseas_stock": {"amount": 0, "profit": 0, "percent": 0},
        "rp": {"amount": 0, "profit": 0, "percent": 0},
        "foreign_currency": {"amount": 0, "profit": 0, "percent": 0},
        "others": {"amount": 0, "profit": 0, "percent": 0}
    }
    
    total_summary = {
        "total_asset_krw": 0,
        "total_pl_krw": 0,
        "total_pchs_krw": 0,
    }

    if integ_res and integ_res.get("rt_cd") == "0":
        # ... (Parsing logic same as before)
        out2 = integ_res.get("output2", {})
        total_summary["total_asset_krw"] = float(out2.get("tot_asst_amt", 0))
        total_summary["total_pl_krw"] = float(out2.get("evlu_pfls_amt_smtl", 0))
        total_summary["total_pchs_krw"] = float(out2.get("pchs_amt_smtl", 0))
        
        out1 = integ_res.get("output1", [])
        
        def parse_category(idx, key):
            if idx < len(out1):
                item = out1[idx]
                asset_classification[key] = {
                    "amount": float(item.get("evlu_amt", 0)),
                    "profit": float(item.get("evlu_pfls_amt", 0)),
                    "percent": float(item.get("whol_weit_rt", 0))
                }

        parse_category(0, "domestic_stock")
        parse_category(7, "rp")
        parse_category(8, "overseas_stock")
        parse_category(16, "foreign_currency")
        
        tracked_sum = (asset_classification["domestic_stock"]["amount"] + 
                       asset_classification["overseas_stock"]["amount"] + 
                       asset_classification["rp"]["amount"] +
                       asset_classification["foreign_currency"]["amount"])
                       
        others_val = total_summary["total_asset_krw"] - tracked_sum
        if others_val > 100: 
             asset_classification["others"]["amount"] = others_val

    # 1.5 Fetch Manual Assets
    manual_assets = db.query(ManualAsset).all()
    manual_holdings = []
    
    for ma in manual_assets:
        # Simple Exchange Rate Logic (Replace with real API later if needed)
        ex_rate = 1400.0 if ma.currency == "USD" else 1.0
        
        val_krw = ma.current_price * ma.quantity * ex_rate
        buy_krw = ma.buy_price * ma.quantity * ex_rate
        profit_krw = val_krw - buy_krw
        
        # Add to totals
        total_summary["total_asset_krw"] += val_krw
        total_summary["total_pl_krw"] += profit_krw
        total_summary["total_pchs_krw"] += buy_krw
        
        # Add to classification
        # Simple mapping: STOCK -> others (or new category?), CASH -> others
        # For now, let's group manual assets into 'others' to keep UI simple, 
        # or we could add them to respective categories if we had a clean way.
        # User asked for manual assets. Let's add them to 'others' for the chart, 
        # but keep them separate in holdings.
        asset_classification["others"]["amount"] += val_krw
        asset_classification["others"]["profit"] += profit_krw
        
        manual_holdings.append({
            "is_manual": True,
            "id": ma.id, # Useful for key
            "symbol": ma.symbol or "MANUAL",
            "name": ma.name,
            "quantity": ma.quantity,
            "avg_price": ma.buy_price,
            "current_price": ma.current_price,
            "pl_amount": profit_krw / ex_rate,
            "return_rate": ((ma.current_price - ma.buy_price) / ma.buy_price * 100) if ma.buy_price > 0 else 0,
            "currency": ma.currency,
            "brokerage": ma.brokerage
        })

    # Recalculate percentages
    if total_summary["total_asset_krw"] > 0:
        for key in asset_classification:
             asset_classification[key]["percent"] = (asset_classification[key]["amount"] / total_summary["total_asset_krw"]) * 100

    # 2. Fetch Holdings Details (Keep existing logic)
    # ... (Rest of existing logic for overseas/domestic holdings)
    # Overseas Holdings
    ov_api = OverseasAPI()
    ov_res = ov_api.get_balance_present()
    ov_holdings = []
    if ov_res and ov_res.get("rt_cd") == "0":
        for item in ov_res.get("output1", []):
            qty = float(item.get("ccld_qty_smtl1", 0))
            if qty > 0:
                ov_holdings.append({
                    "symbol": item.get("pdno"),
                    "name": item.get("prdt_name"),
                    "quantity": qty,
                    "avg_price": float(item.get("avg_unpr3", 0)),
                    "current_price": float(item.get("ovrs_now_pric1", 0)),
                    "pl_amount": float(item.get("evlu_pfls_amt2", 0)),
                    "return_rate": clean_profit_rate(item.get("evlu_pfls_rt1", 0)),
                    "currency": "USD",
                    "brokerage": "Korea Investment"
                })

    # Domestic Holdings
    dom_res_stocks = dom_api.get_balance()
    dom_holdings = []
    if dom_res_stocks and dom_res_stocks.get("rt_cd") == "0":
        for item in dom_res_stocks.get("output1", []):
            qty = float(item.get("hldg_qty", 0))
            if qty > 0:
                dom_holdings.append({
                    "symbol": item.get("pdno"),
                    "name": item.get("prdt_name"),
                    "quantity": qty,
                    "avg_price": float(item.get("pchs_avg_pric", 0)),
                    "current_price": float(item.get("prpr", 0)),
                    "pl_amount": float(item.get("evlu_pfls_amt", 0)),
                    "return_rate": clean_profit_rate(item.get("evlu_pfls_rt", 0)),
                    "currency": "KRW",
                    "brokerage": "Korea Investment"
                })

    # 3. Cash Equivalents (RP, Foreign Currency)
    cash_holdings = []
    
    # RP
    rp_asset = asset_classification.get("rp", {})
    if rp_asset.get("amount", 0) > 0:
        cash_holdings.append({
            "symbol": "RP_MMW",
            "name": "RP / Notes",
            "quantity": 1,
            "avg_price": rp_asset.get("amount", 0), 
            "current_price": rp_asset.get("amount", 0),
            "pl_amount": rp_asset.get("profit", 0),
            "return_rate": 0.0, 
            "currency": "KRW",
            "brokerage": "Korea Investment"
        })

    # Foreign Currency
    fx_asset = asset_classification.get("foreign_currency", {})
    if fx_asset.get("amount", 0) > 0:
         cash_holdings.append({
            "symbol": "FX_USD",
            "name": "Foreign Currency (USD)",
            "quantity": 1,
            "avg_price": fx_asset.get("amount", 0),
            "current_price": fx_asset.get("amount", 0),
            "pl_amount": fx_asset.get("profit", 0),
            "return_rate": 0.0,
            "currency": "KRW",
            "brokerage": "Korea Investment"
        })

    return {
        "summary": total_summary,
        "assets": asset_classification,
        "holdings": {
            "overseas": ov_holdings,
            "domestic": dom_holdings,
            "cash": cash_holdings,
            "manual": manual_holdings
        }
    }

