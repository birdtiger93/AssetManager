from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.database.engine import get_db
from src.database.models import ManualAsset
from src.database.utils import get_or_create_instrument, map_manual_asset_type

router = APIRouter(prefix="/api/assets/manual", tags=["manual_assets"])

# Pydantic Schemas
class ManualAssetCreate(BaseModel):
    asset_type: str
    name: str
    symbol: Optional[str] = None
    quantity: float
    buy_price: float
    current_price: float
    currency: str = "KRW"
    brokerage: str = "Manual"

class ManualAssetUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    buy_price: Optional[float] = None
    current_price: Optional[float] = None
    currency: Optional[str] = None
    brokerage: Optional[str] = None

class ManualAssetResponse(ManualAssetCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

@router.get("/", response_model=List[ManualAssetResponse])
def get_manual_assets(db: Session = Depends(get_db)):
    """List all manually added assets."""
    return db.query(ManualAsset).all()

@router.post("/", response_model=ManualAssetResponse)
def create_manual_asset(asset: ManualAssetCreate, db: Session = Depends(get_db)):
    """Create a new manual asset and register it in instruments table."""
    # Create manual asset record
    new_asset = ManualAsset(
        asset_type=asset.asset_type,
        name=asset.name,
        symbol=asset.symbol,
        quantity=asset.quantity,
        buy_price=asset.buy_price,
        current_price=asset.current_price,
        currency=asset.currency,
        brokerage=asset.brokerage
    )
    db.add(new_asset)
    
    # Also register in instruments table for immediate availability
    asset_type_enum = map_manual_asset_type(asset.asset_type)
    get_or_create_instrument(
        db=db,
        symbol=asset.symbol or f"MANUAL_{new_asset.name}",  # Generate symbol if none
        name=asset.name,
        asset_type=asset_type_enum,
        currency=asset.currency,
        brokerage=asset.brokerage if asset.brokerage != "Manual" else None
    )
    
    db.commit()
    db.refresh(new_asset)
    return new_asset

@router.put("/{asset_id}", response_model=ManualAssetResponse)
def update_manual_asset(asset_id: int, asset_update: ManualAssetUpdate, db: Session = Depends(get_db)):
    """Update an existing manual asset."""
    db_asset = db.query(ManualAsset).filter(ManualAsset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for key, value in asset_update.dict(exclude_unset=True).items():
        setattr(db_asset, key, value)
    
    db.commit()
    db.refresh(db_asset)
    return db_asset

@router.delete("/{asset_id}")
def delete_manual_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete a manual asset."""
    db_asset = db.query(ManualAsset).filter(ManualAsset.id == asset_id).first()
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(db_asset)
    db.commit()
    return {"message": "Asset deleted successfully"}
