"""Database utility functions for instrument management."""
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import Instrument, AssetType


def get_or_create_instrument(db: Session, symbol, name, asset_type, currency="KRW", brokerage=None, exchange=None):
    """Find or create an instrument in the master table."""
    # Search by symbol + asset_type (most reliable combo)
    query = db.query(Instrument).filter(
        Instrument.symbol == symbol,
        Instrument.asset_type == asset_type
    )
    if brokerage:
        query = query.filter(Instrument.brokerage == brokerage)
    
    instrument = query.first()
    
    if instrument:
        # Update name if changed
        if name and instrument.name != name:
            instrument.name = name
            instrument.updated_at = datetime.utcnow()
        return instrument
    
    # Create new instrument
    instrument = Instrument(
        symbol=symbol,
        name=name or symbol,
        asset_type=asset_type,
        currency=currency,
        brokerage=brokerage,
        exchange=exchange
    )
    db.add(instrument)
    db.flush()  # Get the ID without committing
    return instrument


def map_manual_asset_type(asset_type_str: str) -> AssetType:
    """Map manual asset type string to AssetType enum."""
    type_map = {
        "STOCK": AssetType.STOCK_DOMESTIC,
        "STOCK_DOMESTIC": AssetType.STOCK_DOMESTIC,
        "STOCK_OVERSEAS": AssetType.STOCK_OVERSEAS,
        "CRYPTO": AssetType.CRYPTO,
        "REAL_ESTATE": AssetType.MANUAL,
        "CASH": AssetType.CASH_KRW,
    }
    return type_map.get(asset_type_str, AssetType.MANUAL)
