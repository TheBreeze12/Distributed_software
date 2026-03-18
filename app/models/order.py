from app.db.base import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import DateTime,String,ForeignKey,DECIMAL
from decimal import Decimal
from datetime import datetime

class Order(Base):
    __tablename__='orders'
    id : Mapped[int] = mapped_column(index=True,primary_key=True)
    u_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    p_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity : Mapped[int] = mapped_column(nullable=False)
    order_amount : Mapped[Decimal] = mapped_column(DECIMAL(10,2),nullable=False)
    status : Mapped[int] = mapped_column(nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
    payment_time: Mapped[datetime] =mapped_column(DateTime,nullable=True,default=None)
    cancelled_time: Mapped[datetime] =mapped_column(DateTime,nullable=True,default=None)
