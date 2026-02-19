from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.web.routers import dashboard, trade, assets, returns, ocr
from src.database.engine import engine, Base
from src.database import models # Ensure models are loaded

from contextlib import asynccontextmanager
from src.scheduler import start_scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.scheduler import snapshot_assets
from src.logic.strategy import run_strategy

# Global scheduler instance
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Scheduler...")
    # Initialize DB Tables
    Base.metadata.create_all(bind=engine)
    
    # Market-close snapshots only (no more hourly)
    scheduler.add_job(snapshot_assets, CronTrigger(hour=15, minute=40), id='domestic_close')
    scheduler.add_job(snapshot_assets, CronTrigger(hour=6, minute=10), id='overseas_close')
    
    # Strategy Scheduler (Every minute for monitoring)
    scheduler.add_job(run_strategy, 'interval', minutes=1, id='strategy_check')
    
    scheduler.start()
    yield
    # Shutdown
    print("Shutting down Scheduler...")
    scheduler.shutdown()

app = FastAPI(title="KIS Asset Manager API", version="1.0.0", lifespan=lifespan)

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(trade.router)
app.include_router(assets.router)
app.include_router(returns.router)
app.include_router(ocr.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "KIS Asset Manager API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("src.web.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()
