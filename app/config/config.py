from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY=os.getenv('SECRET_KEY')
ACCESS_EXPIRE_MINUTES = 60
ALGORITHM='HS256'
