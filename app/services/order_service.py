from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.crud import order as order_crud
from app.crud.product import get_product_by_name
from app.services import inventory_service
from app.services import kafka_order_service
from app.services import redis_service
from app.services.id_generator import generate_order_id
from datetime import datetime
PEND_PAYMENT=0
PAID=1
CANCELLED=4

# 下单:商品u_id,p_name->pid ,quantity,amount,
def create_order(db:Session,u_id:int,p_name:str,quantity:int):
    product=get_product_by_name(db,p_name)
    if not product:
        raise HTTPException(status_code=404,detail="商品不存在")

    ok,msg = redis_service.reserve_seckill_stock(u_id=u_id,p_id=product.id,quantity=quantity)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=msg)

    order_id = generate_order_id()
    order_amount = float(product.price * quantity)
    payload = {
        "order_id": order_id,
        "u_id": u_id,
        "p_id": product.id,
        "quantity": quantity,
        "order_amount": order_amount,
    }

    try:
        kafka_order_service.publish_order_created_event(payload)
    except Exception as e:  # noqa: BLE001
        redis_service.rollback_seckill_reservation(u_id=u_id,p_id=product.id,quantity=quantity)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"下单排队失败: {e}",
        )

    return {
        "order_id": order_id,
        "status": "PROCESSING",
        "u_id": u_id,
        "p_id": product.id,
        "quantity": quantity,
    }

def get_user_order(db:Session,u_id:int):
    orders=order_crud.get_orders_by_uid(db,u_id)
    return orders

def get_order_by_id(db:Session,id:int):
    return order_crud.get_order_by_id(db,id)


def get_order_by_order_id(db:Session,order_id:str):
    return order_crud.get_order_by_order_id(db,order_id)


def get_orders_by_user_id(db:Session,u_id:int):
    return order_crud.get_orders_by_uid(db,u_id)


def pay_order(db: Session, order_id: str):
    order = order_crud.get_order_by_order_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='订单没有找到')
    if order.status == PAID:
        return {
            "order_id": order_id,
            "status": "PAID",
            "message": "订单已支付",
        }
    if order.status == CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='订单已取消，无法支付')

    try:
        kafka_order_service.publish_order_paid_event({"order_id": order_id})
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"支付请求发送失败: {e}",
        )

    return {
        "order_id": order_id,
        "status": "PAYING",
        "message": "支付处理中",
    }

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
    redis_service.increase_stock_cache(order.p_id,order.quantity)
    return order
