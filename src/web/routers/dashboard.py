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
    Returns the aggregated portfolio summary.
    """
    
    # 1. Overseas
    ov_api = OverseasAPI()
    ov_res = ov_api.get_balance_present()
    
    ov_summary = {}
    ov_holdings = []
    
    if ov_res and ov_res.get("rt_cd") == "0":
        summary_raw = ov_res.get("output3", {})
        # Convert scientific notation strings to floats
        ov_summary = {
            "total_eval_usd": float(summary_raw.get('evlu_amt_smtl', 0)),
            "total_pl_usd": float(summary_raw.get('evlu_pfls_amt_smtl', 0)),
            "total_eval_krw": float(summary_raw.get('evlu_amt_smtl_amt', 0)), # Converted
            "unrealized_pl_krw": float(summary_raw.get('tot_evlu_pfls_amt', 0)),
            "return_rate": clean_profit_rate(summary_raw.get('evlu_erng_rt1', 0))
        }
        
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

    # 2. Domestic
    dom_api = DomesticAPI()
    dom_res = dom_api.get_balance()
    
    dom_summary = {}
    dom_holdings = []
    
    if dom_res and dom_res.get("rt_cd") == "0":
        summary_raw = dom_res.get("output2", [])
        if summary_raw:
            s = summary_raw[0]
            dom_summary = {
                "total_eval_krw": float(s.get('tot_evlu_amt', 0)),
                "unrealized_pl_krw": float(s.get('evlu_pfls_smtl_amt', 0)),
                "pchs_amt": float(s.get('pchs_amt_smtl_amt', 0)), # Purchase amount
            }
            # Calculate return rate manually if not provided clearly or use provided
            # domestic API often provides return rate per stock, aggregate might need calculation
            if dom_summary["pchs_amt"] > 0:
                 dom_summary['return_rate'] = (dom_summary["unrealized_pl_krw"] / dom_summary["pchs_amt"]) * 100
            else:
                 dom_summary['return_rate'] = 0.0

        for item in dom_res.get("output1", []):
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

    # 3. Aggregate
    total_krw = ov_summary.get("total_eval_krw", 0) + dom_summary.get("total_eval_krw", 0)
    total_pl_krw = ov_summary.get("unrealized_pl_krw", 0) + dom_summary.get("unrealized_pl_krw", 0)
    
    return {
        "summary": {
            "total_asset_krw": total_krw,
            "total_pl_krw": total_pl_krw,
            "overseas": ov_summary,
            "domestic": dom_summary
        },
        "holdings": {
            "overseas": ov_holdings,
            "domestic": dom_holdings
        }
    }
