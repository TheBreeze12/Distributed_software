from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.inventory import Inventory
from app.models.product import Product
from fastapi import HTTPException,status
from decimal import Decimal
from app.crud import order as order_crud
from app.crud.product import get_product_by_name
from app.services import inventory_service
from datetime import datetime
PEND_PAYMENT=0
PAID=1
CANCELLED=4

# 下单:商品u_id,p_name->pid ,quantity,amount,
def create_order(db:Session,u_id:int,p_name:str,quantity:int):
    product=get_product_by_name(db,p_name)
    if not product:
        raise HTTPException(status_code=404,detail="商品不存在")

    re=inventory_service.deduct_inventory(db,product.id,quantity)
    if re==False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='扣除库存失败')

    order_amount=product.price*quantity
    order=order_crud.create_order(db,u_id,product.id,quantity,order_amount,status=PEND_PAYMENT)
    return order

def get_user_order(db:Session,u_id:int):
    orders=order_crud.get_orders_by_uid(db,u_id)
    return orders

def get_order_by_id(db:Session,id:int):
    return order_crud.get_order_by_id(db,id)

def confirm_order(db,o_id):
    order=order_crud.update_order(db,o_id,status=PAID,
                            updated_at=datetime.utcnow(),
                            payment_time=datetime.utcnow())
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='订单没有找到')
    return order


def cancel_order(db,o_id):
    order=order_crud.update_order(db,o_id,status=CANCELLED,
                                  updated_at=datetime.utcnow(),
                                  cancelled_time=datetime.utcnow())
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='订单没有找到')

    # ✅ 发送消息到队列（库存服务需要回滚）
    # await publish_event('order.cancelled', {
    #     'order_id': order.order_id,
    #     'product_id': order.product_id,
    #     'quantity': order.quantity
    # })
    re=inventory_service.rollback_inventory(db,order.p_id,order.quantity)
    if not re:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='取消失败')
    return order
