from app.db.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,DateTime,DECIMAL
from datetime import datetime
from decimal import Decimal

class Product(Base):
    __tablename__='products'
    id : Mapped[int] = mapped_column(primary_key=True,index=True)
    name : Mapped[str] = mapped_column(String(32),index=True,nullable=False,unique=True)
    price : Mapped[Decimal] = mapped_column(DECIMAL(10,2),nullable=False,default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
