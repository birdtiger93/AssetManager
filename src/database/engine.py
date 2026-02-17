from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_URL = f"sqlite:///{os.path.join(DATA_DIR, 'assets.db')}"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
