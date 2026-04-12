from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services import kafka_order_service


def _build_session_local():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def test_process_order_message_success_and_idempotent(monkeypatch):
    SessionLocal = _build_session_local()
    monkeypatch.setattr(kafka_order_service, "WriteSessionLocal", SessionLocal)

    db = SessionLocal()
    db.add(User(username="u1", password_hash="x", email="u1@test.com"))
    db.add(Product(id=1, name="p1", price=Decimal("9.90")))
    db.add(Inventory(p_id=1, total_stock=10, available_stock=10, locked_stock=0))
    db.commit()
    db.close()

    called = []
    monkeypatch.setattr(kafka_order_service.redis_service, "rollback_seckill_reservation", lambda **kwargs: called.append(kwargs) or True)

    payload = {
        "order_id": "10001",
        "u_id": 1,
        "p_id": 1,
        "quantity": 2,
        "order_amount": "19.80",
    }
    kafka_order_service.process_order_message(payload)
    kafka_order_service.process_order_message(payload)

    db = SessionLocal()
    orders = db.query(Order).all()
    inventory = db.query(Inventory).filter(Inventory.p_id == 1).first()
    db.close()

    assert len(orders) == 1
    assert orders[0].order_id == "10001"
    assert inventory.available_stock == 8
    assert inventory.locked_stock == 2
    assert called == []


def test_process_order_message_rollback_when_db_stock_insufficient(monkeypatch):
    SessionLocal = _build_session_local()
    monkeypatch.setattr(kafka_order_service, "WriteSessionLocal", SessionLocal)

    db = SessionLocal()
    db.add(User(username="u2", password_hash="x", email="u2@test.com"))
    db.add(Product(id=2, name="p2", price=Decimal("10.00")))
    db.add(Inventory(p_id=2, total_stock=1, available_stock=1, locked_stock=0))
    db.commit()
    db.close()

    called = []
    monkeypatch.setattr(kafka_order_service.redis_service, "rollback_seckill_reservation", lambda **kwargs: called.append(kwargs) or True)

    payload = {
        "order_id": "10002",
        "u_id": 1,
        "p_id": 2,
        "quantity": 2,
        "order_amount": "20.00",
    }

    try:
        kafka_order_service.process_order_message(payload)
    except ValueError as e:
        assert "insufficient db stock" in str(e)

    db = SessionLocal()
    orders = db.query(Order).all()
    db.close()

    assert orders == []
    assert len(called) == 1


def test_process_order_paid_message_success_and_idempotent(monkeypatch):
    SessionLocal = _build_session_local()
    monkeypatch.setattr(kafka_order_service, "WriteSessionLocal", SessionLocal)

    db = SessionLocal()
    db.add(User(id=10, username="u10", password_hash="x", email="u10@test.com"))
    db.add(Product(id=10, name="p10", price=Decimal("20.00")))
    db.add(Inventory(p_id=10, total_stock=10, available_stock=8, locked_stock=2))
    db.add(
        Order(
            order_id="pay10001",
            u_id=10,
            p_id=10,
            quantity=2,
            order_amount=Decimal("40.00"),
            status=0,
        )
    )
    db.commit()
    db.close()

    kafka_order_service.process_order_paid_message({"order_id": "pay10001"})
    kafka_order_service.process_order_paid_message({"order_id": "pay10001"})

    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == "pay10001").first()
    inven = db.query(Inventory).filter(Inventory.p_id == 10).first()
    db.close()

    assert order.status == 1
    assert order.payment_time is not None
    assert inven.available_stock == 8
    assert inven.locked_stock == 0


def test_process_order_paid_message_fail_when_locked_stock_insufficient(monkeypatch):
    SessionLocal = _build_session_local()
    monkeypatch.setattr(kafka_order_service, "WriteSessionLocal", SessionLocal)

    db = SessionLocal()
    db.add(User(id=11, username="u11", password_hash="x", email="u11@test.com"))
    db.add(Product(id=11, name="p11", price=Decimal("20.00")))
    db.add(Inventory(p_id=11, total_stock=10, available_stock=8, locked_stock=1))
    db.add(
        Order(
            order_id="pay10002",
            u_id=11,
            p_id=11,
            quantity=2,
            order_amount=Decimal("40.00"),
            status=0,
        )
    )
    db.commit()
    db.close()

    try:
        kafka_order_service.process_order_paid_message({"order_id": "pay10002"})
    except ValueError as e:
        assert "insufficient locked stock" in str(e)

    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == "pay10002").first()
    inven = db.query(Inventory).filter(Inventory.p_id == 11).first()
    db.close()

    assert order.status == 0
    assert order.payment_time is None
    assert inven.locked_stock == 1
