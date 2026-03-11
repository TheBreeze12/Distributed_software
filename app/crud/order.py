from sqlalchemy.orm import Session
from app.models.order import Order
from decimal import Decimal

def create_order(db:Session,u_id:int, p_id:int,quantity:int,order_amount:Decimal,status:int):
    order=Order(u_id,p_id,quantity,order_amount,status)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def delete_order(db:Session,id:int):
    order=db.query(Order).filter(Order.id==id).first()
    if order:
        db.delete(order)
        db.commit()
        return True
    return False

def update_order(db:Session,id:int ,**kwargs):
    order=db.query(Order).filter(Order.id==id).first()
    if not order:
        return None
    for key , value in kwargs.items():
        if hasattr(order,key):
            setattr(order,key,value)
    db.commit()
    db.refresh(order)
    return order

def get_orders_by_uid(db:Session,u_id:int):
    orders=db.query(Order).filter(Order.u_id==u_id).all()
    return orders

def get_order_by_id(db:Session,id:int):
    order=db.query(Order).filter(Order.id==id).first()
    return order
