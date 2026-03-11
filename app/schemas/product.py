from pydantic import BaseModel,Field
from app.models.product import Product
from typing import List,Optional
from datetime import datetime
from decimal import Decimal

class ProductSchema(BaseModel):
    id: int
    name: str
    price: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductAddRequest(BaseModel):
    name:str = Field(...,min_length=1)
    price:Decimal = Field(...,gt=0)

class ProductResponse(BaseModel):
    msg : str
    code : int
    data : ProductSchema | List[ProductSchema] | None
