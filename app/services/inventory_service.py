from sqlalchemy.orm import Session
from app.crud import inventory
from fastapi import HTTPException,status
from app.core.redis_client import redis_client
import json
def get_inventory_by_pid(db:Session,p_id:int):
    key=f"stock:product:{p_id}"
    inven=redis_client.get(key)
    if inven:
        data=json.loads(inven)
        print("从redis中获取库存数据")
        return data
    inven=inventory.get_inventory_by_pid(db,p_id)
    return inven

def deduct_inventory(db:Session,p_id:int,quantity:int):
    inven=inventory.get_inventory_by_pid(db,p_id)
    if not inven :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='没有找到商品库存')
    if inven.available_stock<quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='库存不足')

    # todo：尝试从Redis扣减

    # 数据库操作
    inventory.update_inventory(db,inven.id,
                            available_stock=inven.available_stock-quantity,
                            locked_stock=inven.locked_stock+quantity )
    return True


def rollback_inventory(db:Session,p_id:int,quantity:int):
    inven=inventory.get_inventory_by_pid(db,p_id)
    if not inven :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='没有找到商品库存')
    inventory.update_inventory(db,inven.id,
                            available_stock=inven.available_stock+quantity,
                            locked_stock=inven.locked_stock-quantity )
    return True
