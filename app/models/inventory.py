from app.db.base import Base
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column


class Inventory(Base):
    __tablename__="inventories"
    id : Mapped[int] = mapped_column(primary_key=True,index=True)
    p_id : Mapped[int] = mapped_column(ForeignKey("products.id"),unique=True,index=True)
    total_stock : Mapped[int] =mapped_column(nullable=True)
    availbale_stock : Mapped[int] =mapped_column(nullable=True)
    locked_stock : Mapped[int] =mapped_column(nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=False)
