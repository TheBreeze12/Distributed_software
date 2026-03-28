import json
import random
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.redis_client import redis_client
from app.crud.product import create_product, get_all_products, get_product_by_id, get_product_by_name
from app.models.product import Product

NULL_CACHE_VALUE = "__NULL__"
NULL_CACHE_TTL = 60
DETAIL_CACHE_TTL = 300
DETAIL_CACHE_JITTER = 60
LIST_CACHE_TTL = 120
LIST_CACHE_JITTER = 30
LOCK_EXPIRE_SEC = 8
LOCK_RETRY_TIMES = 20
LOCK_WAIT_SEC = 0.05


def _serialize_product(product: Product):
    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def _cache_set_json(key: str, value, ttl: int, jitter: int = 0):
    expire = ttl + random.randint(0, jitter) if jitter > 0 else ttl
    redis_client.setex(key, expire, json.dumps(value))


def _release_lock(lock_key: str, token: str):
    script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""
    redis_client.eval(script, 1, lock_key, token)


def _query_detail_with_lock(db: Session, product_id: int, key: str):
    lock_key = f"lock:product:id:{product_id}"
    token = f"{time.time()}-{random.randint(1000, 9999)}"

    for _ in range(LOCK_RETRY_TIMES):
        cached = redis_client.get(key)
        if cached is not None:
            if cached == NULL_CACHE_VALUE:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
            return json.loads(cached)

        got_lock = redis_client.set(lock_key, token, nx=True, ex=LOCK_EXPIRE_SEC)
        if got_lock:
            try:
                cached = redis_client.get(key)
                if cached is not None:
                    if cached == NULL_CACHE_VALUE:
                        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
                    return json.loads(cached)

                product = get_product_by_id(db, product_id)
                if not product:
                    redis_client.setex(key, NULL_CACHE_TTL, NULL_CACHE_VALUE)
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

                data = _serialize_product(product)
                _cache_set_json(key, data, DETAIL_CACHE_TTL, DETAIL_CACHE_JITTER)
                return data
            finally:
                _release_lock(lock_key, token)

        time.sleep(LOCK_WAIT_SEC)

    product = get_product_by_id(db, product_id)
    if not product:
        redis_client.setex(key, NULL_CACHE_TTL, NULL_CACHE_VALUE)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    data = _serialize_product(product)
    _cache_set_json(key, data, DETAIL_CACHE_TTL, DETAIL_CACHE_JITTER)
    return data


def _query_list_with_lock(db: Session, key: str):
    lock_key = "lock:product:all"
    token = f"{time.time()}-{random.randint(1000, 9999)}"

    for _ in range(LOCK_RETRY_TIMES):
        cached = redis_client.get(key)
        if cached is not None:
            return json.loads(cached)

        got_lock = redis_client.set(lock_key, token, nx=True, ex=LOCK_EXPIRE_SEC)
        if got_lock:
            try:
                cached = redis_client.get(key)
                if cached is not None:
                    return json.loads(cached)

                products = get_all_products(db)
                data = [_serialize_product(p) for p in products]
                _cache_set_json(key, data, LIST_CACHE_TTL, LIST_CACHE_JITTER)
                return data
            finally:
                _release_lock(lock_key, token)

        time.sleep(LOCK_WAIT_SEC)

    products = get_all_products(db)
    data = [_serialize_product(p) for p in products]
    _cache_set_json(key, data, LIST_CACHE_TTL, LIST_CACHE_JITTER)
    return data


def invalidate_product_cache(product_id: int | None = None, name: str | None = None):
    keys = ["product:all"]
    if product_id is not None:
        keys.append(f"product:id:{product_id}")
    if name:
        keys.append(f"product:name:{name}")
    redis_client.delete(*keys)


def get_product_service(db: Session, id: int | None = None):
    if id is None:
        key = "product:all"
        cached = redis_client.get(key)
        if cached is not None:
            return json.loads(cached)
        return _query_list_with_lock(db, key)

    key = f"product:id:{id}"
    cached = redis_client.get(key)
    if cached is not None:
        if cached == NULL_CACHE_VALUE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
        return json.loads(cached)

    return _query_detail_with_lock(db, id, key)


def get_product_name_service(db: Session, name: str):
    key = f"product:name:{name}"
    cached = redis_client.get(key)
    if cached is not None:
        if cached == NULL_CACHE_VALUE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
        return json.loads(cached)

    product = get_product_by_name(db, name)
    if not product:
        redis_client.setex(key, NULL_CACHE_TTL, NULL_CACHE_VALUE)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    data = _serialize_product(product)
    _cache_set_json(key, data, DETAIL_CACHE_TTL, DETAIL_CACHE_JITTER)
    return data


def add_product_service(db: Session, name: str, price: float):
    product = get_product_by_name(db, name)
    if product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该商品已存在")

    created = create_product(db, name, price)
    invalidate_product_cache()
    return created
