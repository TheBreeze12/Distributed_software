from sqlalchemy.orm import Session
from app.models.product import Product
from app.crud.product import get_all_products,get_product_by_id,get_product_by_name,create_product
from fastapi import HTTPException,status

def get_product_service(db:Session,id: int | None = None):
    if id is None:
        products=get_all_products(db)
        return products
    product = get_product_by_id(db,id)
    return product


def get_product_name_service(db : Session, name :str):
    return get_product_by_name(db,name)



def add_product_service(db:Session,name:str,price:float):
    product=get_product_by_name(db,name)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='该商品已存在')
    return create_product(db,name,price)
