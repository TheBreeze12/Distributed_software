from app.db.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy  import String , DateTime
from datetime import datetime

class User(Base):
    __tablename__="users"
    id : Mapped[int] = mapped_column(primary_key=True,index=True)
    username : Mapped[str] = mapped_column(String(32),index=True,unique=True,nullable=False)
    password_hash : Mapped[str] = mapped_column(String(255),nullable=False)
    email : Mapped[str] = mapped_column(String(40),nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
