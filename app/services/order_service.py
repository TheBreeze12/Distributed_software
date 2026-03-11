from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.inventory import Inventory
from app.models.product import Product
from fastapi import HTTPException
from decimal import Decimal
from app.crud import order as order_crud
from app.crud.inventory import update_inventory,get_inventory_by_pid
from app.crud.product import get_product_by_name
# 下单:商品u_id,p_name->pid ,quantity,amount,
def create_order(db:Session,u_id:int,p_name:str,quantity:int):
    product=get_product_by_name(db,p_name)
    if not product:
        raise HTTPException(status_code=404,detail="商品不存在")
    inven=get_inventory_by_pid(db,product.id)
    if not inven or inven.available_stock<quantity:
        raise HTTPException(status_code=400,detail="库存不足")

    order_amount=product.price*quantity
    order=order_crud.create_order(db,u_id,product.id,quantity,order_amount,status=0)
    update_inventory(db,inven.id,available_stock=inven.available_stock-quantity,locked_stock=inven.locked_stock+quantity)
    return order

def get_user_order(db:Session,u_id:int):
    orders=order_crud.get_orders_by_uid(db,u_id)
    return orders

def get_order_by_id(db:Session,id:int):
    return order_crud.get_order_by_id(db,id)
