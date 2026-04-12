from pydantic import BaseModel,Field,ConfigDict
from typing import List
from decimal import Decimal
from datetime import datetime
class OrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id :  int
    order_id: str
    u_id :  int
    p_id :  int
    quantity :  int
    order_amount :  Decimal
    status :  int
    created_at :  datetime
    updated_at :  datetime
    payment_time:datetime|None=None
    cancelled_time:datetime|None=None

class OrderResponse(BaseModel):
    msg:str
    code:int
    data:OrderSchema|List[OrderSchema]|None

class OrderCreateRequest(BaseModel):
    p_name : str = Field(...,description="商品名")
    quantity: int = Field(gt=0)


class OrderCreateAccepted(BaseModel):
    order_id: str
    status: str
    u_id: int
    p_id: int
    quantity: int


class OrderCreateResponse(BaseModel):
    msg: str
    code: int
    data: OrderCreateAccepted
