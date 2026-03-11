from datetime import datetime,timezone,timedelta
from jose import jwt
import os
from app.config.config import ACCESS_EXPIRE_MINUTES,SECRET_KEY,ALGORITHM
from passlib.context import CryptContext


pwd_content=CryptContext(schemes=["bcrypt"],deprecated='auto')

def hash_password(password:str):
    password = password[:72]  # bcrypt 限制
    return pwd_content.hash(password)

def verify_password(password:str,password_hash):
    password = password[:72]
    return pwd_content.verify(password,password_hash)

def create_access_token(subject:int,expire_time=ACCESS_EXPIRE_MINUTES):
    expire = datetime.now(timezone.utc)+timedelta(minutes=expire_time)
    pay_load={'sub':subject,'exp':expire}
    return jwt.encode(pay_load,algorithm=ALGORITHM,key=SECRET_KEY)
