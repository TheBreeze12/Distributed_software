from app.services import redis_service


class FakeRedis:
    def __init__(self):
        self.store = {}

    def eval(self, script, numkeys, *args):
        stock_key, user_key = args[0], args[1]
        quantity = int(args[2])

        if "EXISTS', KEYS[2]" in script and "DECRBY" in script:
            if user_key in self.store:
                return -2
            stock = int(self.store.get(stock_key, -1))
            if stock < 0:
                return -3
            if stock < quantity:
                return -1
            self.store[stock_key] = stock - quantity
            self.store[user_key] = "1"
            return 1

        if "INCRBY" in script and "DEL" in script:
            if user_key not in self.store:
                return 0
            stock = int(self.store.get(stock_key, 0))
            self.store[stock_key] = stock + quantity
            del self.store[user_key]
            return 1

        raise RuntimeError("unexpected script")

    def incrby(self, key, value):
        self.store[key] = int(self.store.get(key, 0)) + int(value)


def test_reserve_stock_and_idempotency(monkeypatch):
    fake = FakeRedis()
    fake.store["stock:count:9"] = 5
    monkeypatch.setattr(redis_service, "redis_client", fake)

    ok, msg = redis_service.reserve_seckill_stock(u_id=1, p_id=9, quantity=2)
    assert ok is True
    assert msg == "ok"
    assert fake.store["stock:count:9"] == 3

    ok, msg = redis_service.reserve_seckill_stock(u_id=1, p_id=9, quantity=1)
    assert ok is False
    assert "只能秒杀一次" in msg


def test_rollback_seckill_reservation(monkeypatch):
    fake = FakeRedis()
    fake.store["stock:count:3"] = 0
    fake.store["seckill:uid:2:pid:3"] = "1"
    monkeypatch.setattr(redis_service, "redis_client", fake)

    ok = redis_service.rollback_seckill_reservation(u_id=2, p_id=3, quantity=1)
    assert ok is True
    assert fake.store["stock:count:3"] == 1
    assert "seckill:uid:2:pid:3" not in fake.store
