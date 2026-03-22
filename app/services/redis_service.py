from app.core.redis_client import redis_client
from sqlalchemy.orm import Session
from app.crud import inventory,order,product
import json
def warm_up_stock_to_redis(db:Session):
    invens:Inv=inventory.get_all_inventory(db)
    for i in invens:
        data={
            "id" : i.id,
            "p_id":i.p_id,
            "total_stock":i.total_stock,
            "available_stock":i.available_stock,
            "locked_stock":i.locked_stock,
            "created_at":i.created_at.isoformat() if i.created_at else None,
            "updated_at":i.updated_at.isoformat() if i.updated_at else None,
        }
        redis_client.set(f"stock:product:{i.p_id}", json.dumps(dict(data)))
    return len(invens)

def warm_up_product_to_redis(db:Session):
    products=product.get_all_products(db)
    datas=[]
    for p in products:
        data={
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        datas.append(data)
        redis_client.set(f"product:id:{p.id}", json.dumps(dict(data)))
        redis_client.set(f"product:name:{p.name}", json.dumps(dict(data)))
    redis_client.set("product:all",json.dumps(datas))
    return len(products)
