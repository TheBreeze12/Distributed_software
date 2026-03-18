from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_username(db:Session,username:str)->User|None:
    return db.query(User).filter(User.username==username).first()

def create_user(db:Session,username:str,password_hash:str,email:str)->User:
    user=User(username=username,password_hash=password_hash,email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db:Session,id : int):
    return db.query(User).filter(User.id==id).first()

def update_user(db:Session,id : int,**kwargs):
    user=db.query(User).filter(User.id==id).first()
    if not user:
        return None
    for key,value in kwargs.items():
        if hasattr(user,key):
            setattr(user,key,value)
    db.commit()
    db.refresh(user)
    return user
