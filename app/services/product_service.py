from sqlalchemy.orm import Session
from app.models.product import Product
from app.crud.product import get_all_products,get_product_by_id,get_product_by_name,create_product
from fastapi import HTTPException,status
from app.core.redis_client import redis_client
import json

def get_product_service(db:Session,id: int | None = None):
    if id is None:
        key="product:all"
        products=redis_client.get(key)
        if products:
            print("从redis中获取商品信息")
            products=json.loads(products)
            return products
        products=get_all_products(db)
        return products
    key=f"product:id:{id}"
    product=redis_client.get(key)
    if product:
        print("从redis中获取商品信息")
        product=json.loads(product)
        return product
    product = get_product_by_id(db,id)
    return product


def get_product_name_service(db : Session, name :str):
    key=f"product:name:{name}"
    product=redis_client.get(key)
    if product:
        print("从redis中获取商品信息")
        product=json.loads(product)
        return product
    return get_product_by_name(db,name)


def add_product_service(db:Session,name:str,price:float):
    product=get_product_by_name(db,name)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='该商品已存在')
    return create_product(db,name,price)
