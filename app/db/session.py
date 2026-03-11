from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DB_HOST=os.getenv("DB_HOST",'localhost')
DB_PORT=os.getenv("DB_PORT",'3306')
DB_USER=os.getenv("DB_USER",'root')
DB_PASSWORD=os.getenv("DB_PASSWORD",'')
DB_NAME=os.getenv("DB_NAME",'commerce')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine= create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)
