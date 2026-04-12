from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.services import order_service


def _build_session_local():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def test_pay_order_publish_paid_event(monkeypatch):
    SessionLocal = _build_session_local()
    db = SessionLocal()
    db.add(User(id=21, username="u21", password_hash="x", email="u21@test.com"))
    db.add(Product(id=21, name="p21", price=Decimal("10.00")))
    db.add(
        Order(
            order_id="biz-pay-1",
            u_id=21,
            p_id=21,
            quantity=1,
            order_amount=Decimal("10.00"),
            status=0,
        )
    )
    db.commit()

    called = []
    monkeypatch.setattr(
        order_service.kafka_order_service,
        "publish_order_paid_event",
        lambda payload: called.append(payload),
    )

    result = order_service.pay_order(db, "biz-pay-1")

    assert result["status"] == "PAYING"
    assert called == [{"order_id": "biz-pay-1"}]

    db.close()


def test_pay_order_idempotent_when_already_paid(monkeypatch):
    SessionLocal = _build_session_local()
    db = SessionLocal()
    db.add(User(id=22, username="u22", password_hash="x", email="u22@test.com"))
    db.add(Product(id=22, name="p22", price=Decimal("10.00")))
    db.add(
        Order(
            order_id="biz-pay-2",
            u_id=22,
            p_id=22,
            quantity=1,
            order_amount=Decimal("10.00"),
            status=1,
        )
    )
    db.commit()

    # 已支付不应再发消息
    monkeypatch.setattr(
        order_service.kafka_order_service,
        "publish_order_paid_event",
        lambda payload: (_ for _ in ()).throw(RuntimeError("should not publish")),
    )

    result = order_service.pay_order(db, "biz-pay-2")
    assert result["status"] == "PAID"

    db.close()
