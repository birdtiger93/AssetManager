from fastapi import APIRouter, HTTPException
import pandas as pd
from typing import Dict, List, Any
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
async def get_dashboard_summary() -> Dict[str, Any]:
    """
    Returns the aggregated portfolio summary using Integrated Account Balance (CTRP6548R).
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
        # Parse Output2 (Totals)
        out2 = integ_res.get("output2", {})
        total_summary["total_asset_krw"] = float(out2.get("tot_asst_amt", 0))
        total_summary["total_pl_krw"] = float(out2.get("evlu_pfls_amt_smtl", 0))
        total_summary["total_pchs_krw"] = float(out2.get("pchs_amt_smtl", 0))
        
        # Parse Output1 (Asset Classes)
        # Index 0: Domestic Stock
        # Index 7: RP
        # Index 8: Overseas Stock
        # Index 16: Foreign Currency
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
        
        # Calculate Others: Total - (Stock + OvStock + RP + FX)
        # Note: 'evlu_amt' for FX (Index 16) might need checking if it is included in total asset correctly. 
        # Usually total_asset includes everything.
        
        tracked_sum = (asset_classification["domestic_stock"]["amount"] + 
                       asset_classification["overseas_stock"]["amount"] + 
                       asset_classification["rp"]["amount"] +
                       asset_classification["foreign_currency"]["amount"])
                       
        others_val = total_summary["total_asset_krw"] - tracked_sum
        if others_val > 100: # Threshold for rounding errors
             asset_classification["others"]["amount"] = others_val
             if total_summary["total_asset_krw"] > 0:
                 asset_classification["others"]["percent"] = (others_val / total_summary["total_asset_krw"]) * 100

    # 2. Fetch Holdings Details (Keep existing logic roughly)
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
                    "currency": "USD"
                })

    # Domestic Holdings
    # We still need to call inquire-balance (TTTC8434R) to get the list of stocks, 
    # as inquire-account-balance (CTRP6548R) doesn't return list of stocks.
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
                    "currency": "KRW"
                })

    return {
        "summary": total_summary,
        "assets": asset_classification,
        "holdings": {
            "overseas": ov_holdings,
            "domestic": dom_holdings
        }
    }
