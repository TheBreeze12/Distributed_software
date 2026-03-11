from app.models.product import Product
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
def get_product_by_id(db : Session,id : int)->Product|None:
    return db.query(Product).filter(Product.id==id).first()


def get_product_by_name(db : Session,name: str)->Product | None:
    return db.query(Product).filter(Product.name==name).first()

def get_all_products(db:Session)->List[Product]|None:
    return db.query(Product).all()

def create_product(db:Session,name:str,price:Decimal)->Product:
    product=Product(name=name,price=price)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
