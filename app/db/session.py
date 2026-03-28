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
DB_READ_HOST = os.getenv("DB_READ_HOST", DB_HOST)
DB_READ_PORT = os.getenv("DB_READ_PORT", DB_PORT)
DB_READ_USER = os.getenv("DB_READ_USER", DB_USER)
DB_READ_PASSWORD = os.getenv("DB_READ_PASSWORD", DB_PASSWORD)
DB_READ_NAME = os.getenv("DB_READ_NAME", DB_NAME)

WRITE_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
READ_DATABASE_URL = f"mysql+pymysql://{DB_READ_USER}:{DB_READ_PASSWORD}@{DB_READ_HOST}:{DB_READ_PORT}/{DB_READ_NAME}?charset=utf8mb4"

write_engine = create_engine(
    WRITE_DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

read_engine = create_engine(
    READ_DATABASE_URL,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False
)

WriteSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=write_engine)
ReadSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=read_engine)

# Backward compatibility: existing code importing engine/SessionLocal still works.
engine = write_engine
SessionLocal = WriteSessionLocal
