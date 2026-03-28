import json
import random

from sqlalchemy.orm import Session

from app.core.redis_client import redis_client
from app.crud import inventory, product

STOCK_CACHE_TTL = 3600
PRODUCT_DETAIL_TTL = 300
PRODUCT_DETAIL_JITTER = 60
PRODUCT_LIST_TTL = 120
PRODUCT_LIST_JITTER = 30


def warm_up_stock_to_redis(db: Session):
    invens = inventory.get_all_inventory(db)
    for i in invens:
        data = {
            "id": i.id,
            "p_id": i.p_id,
            "total_stock": i.total_stock,
            "available_stock": i.available_stock,
            "locked_stock": i.locked_stock,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        }
        redis_client.setex(f"stock:product:{i.p_id}", STOCK_CACHE_TTL, json.dumps(data))
    return len(invens)


def warm_up_product_to_redis(db: Session):
    products = product.get_all_products(db)
    datas = []
    for p in products:
        data = {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        datas.append(data)
        detail_ttl = PRODUCT_DETAIL_TTL + random.randint(0, PRODUCT_DETAIL_JITTER)
        redis_client.setex(f"product:id:{p.id}", detail_ttl, json.dumps(data))
        redis_client.setex(f"product:name:{p.name}", detail_ttl, json.dumps(data))

    list_ttl = PRODUCT_LIST_TTL + random.randint(0, PRODUCT_LIST_JITTER)
    redis_client.setex("product:all", list_ttl, json.dumps(datas))
    return len(products)
