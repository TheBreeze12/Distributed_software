from app.crud.user import get_user_by_username,update_user,create_user,get_user_by_id
from app.models.user import User
from sqlalchemy.orm import Session
from app.core.security import verify_password,hash_password,create_access_token
from fastapi import HTTPException,status,Request,Depends
from jose import jwt, JWTError
from app.config.config import ALGORITHM,SECRET_KEY
from app.api.deps import get_db

def login(db:Session, username:str, password:str ):
    user:User=get_user_by_username(db,username)
    if user is None or not verify_password(password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='用户名或密码错误')
    return create_access_token(subject=str(user.id))

def register(db:Session,username:str,password:str,email:str):
    user = get_user_by_username(db,username)
    print(user)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="用户已经存在")
    return create_user(db,username,hash_password(password),email)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header=request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="未提供token")
    token=auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get('sub')
        if not user_id :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='token无效')
        user=get_user_by_id(db,user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="没有找到用户")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='token无效')


def change_user_password(password_old,password_new,id:int,db:Session,):
    user=get_user_by_id(db,id)
    if not user or not verify_password(password_old,user.password_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='用户或者密码错误')
    password_new=hash_password(password_new)
    user=update_user(db,id,password_hash=password_new)
    return user


def change_user_info(id:int,db:Session,**kwargs):
    if 'password' in kwargs.keys():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='无法修改密码')
    if 'username' in kwargs.keys():
        username=kwargs.get('username')
        user=get_user_by_username(db,username)
        if user :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='用户名被别人使用')
    user=update_user(db,id,**kwargs)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='没有找到这个用户')
    return user
