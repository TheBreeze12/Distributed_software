from pydantic import BaseModel
from datetime import datetime


class InventorySchema(BaseModel):
    id :  int
    p_id :  int
    total_stock:int
    available_stock : int
    locked_stock:int
    created_at :  datetime
    updated_at :  datetime


class InventoryResponse(BaseModel):
    msg:str
    code:int
    data: InventorySchema |None
