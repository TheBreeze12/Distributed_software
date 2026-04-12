import json
import random
from typing import Tuple

from sqlalchemy.orm import Session

from app.core.redis_client import redis_client
from app.crud import inventory, product

STOCK_CACHE_TTL = 3600
PRODUCT_DETAIL_TTL = 300
PRODUCT_DETAIL_JITTER = 60
PRODUCT_LIST_TTL = 120
PRODUCT_LIST_JITTER = 30

SECKILL_DEDUCT_LUA = """
if redis.call('EXISTS', KEYS[2]) == 1 then
    return -2
end
local stock = tonumber(redis.call('GET', KEYS[1]) or '-1')
if stock < 0 then
    return -3
end
if stock < tonumber(ARGV[1]) then
    return -1
end
redis.call('DECRBY', KEYS[1], ARGV[1])
redis.call('SET', KEYS[2], ARGV[2])
return 1
"""

SECKILL_ROLLBACK_LUA = """
if redis.call('EXISTS', KEYS[2]) == 0 then
    return 0
end
redis.call('INCRBY', KEYS[1], ARGV[1])
redis.call('DEL', KEYS[2])
return 1
"""


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
        redis_client.set(f"stock:count:{i.p_id}", int(i.available_stock))
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


def reserve_seckill_stock(u_id: int, p_id: int, quantity: int) -> Tuple[bool, str]:
    stock_key = f"stock:count:{p_id}"
    user_key = f"seckill:uid:{u_id}:pid:{p_id}"
    result = int(redis_client.eval(SECKILL_DEDUCT_LUA, 2, stock_key, user_key, quantity, "1"))

    if result == 1:
        return True, "ok"
    if result == -1:
        return False, "库存不足"
    if result == -2:
        return False, "同一用户同一商品只能秒杀一次"
    return False, "库存缓存未预热"


def rollback_seckill_reservation(u_id: int, p_id: int, quantity: int) -> bool:
    stock_key = f"stock:count:{p_id}"
    user_key = f"seckill:uid:{u_id}:pid:{p_id}"
    result = int(redis_client.eval(SECKILL_ROLLBACK_LUA, 2, stock_key, user_key, quantity))
    return result == 1


def increase_stock_cache(p_id: int, quantity: int) -> None:
    redis_client.incrby(f"stock:count:{p_id}", quantity)
