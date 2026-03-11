from pydantic import BaseModel
from typing import List
class OrderSchema(BaseModel):
    pass

class OrderResponse(BaseModel):
    msg:str
    code:int
    data:OrderSchema|List[OrderSchema]|None

class OrderCreateRequest(BaseModel):
    pass
