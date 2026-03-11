from pydantic import BaseModel,Field
from typing import List
from decimal import Decimal
from datetime import datetime
class OrderSchema(BaseModel):
    id :  int
    u_id :  int
    p_id :  int
    quantity :  int
    order_amount :  Decimal
    status :  int
    created_at :  datetime
    updated_at :  datetime


class OrderResponse(BaseModel):
    msg:str
    code:int
    data:OrderSchema|List[OrderSchema]|None

class OrderCreateRequest(BaseModel):
    p_name : str = Field(...,description="商品名")
    quantity: int = Field(gt=0)
