import json
import logging
import os
import threading
import time
from decimal import Decimal

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from app.db.session import WriteSessionLocal
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.product import Product
from app.services import redis_service

logger = logging.getLogger(__name__)

KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "true").lower() == "true"
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
KAFKA_ORDER_TOPIC = os.getenv("KAFKA_ORDER_TOPIC", "seckill-order-create")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "seckill-order-workers")

_producer = None
_consumer_thread = None
_stop_event = threading.Event()


class KafkaUnavailableError(RuntimeError):
    pass


def _build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=3,
        acks="all",
    )


def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = _build_producer()
    return _producer


def publish_order_created_event(payload: dict) -> None:
    if not KAFKA_ENABLED:
        raise KafkaUnavailableError("Kafka disabled")
    producer = get_producer()
    future = producer.send(KAFKA_ORDER_TOPIC, payload)
    future.get(timeout=10)
    producer.flush(timeout=10)


def process_order_message(payload: dict) -> None:
    required_fields = ["order_id", "u_id", "p_id", "quantity", "order_amount"]
    if any(field not in payload for field in required_fields):
        raise ValueError("order payload missing required fields")

    order_id = str(payload["order_id"])
    u_id = int(payload["u_id"])
    p_id = int(payload["p_id"])
    quantity = int(payload["quantity"])
    order_amount = Decimal(str(payload["order_amount"]))

    db = WriteSessionLocal()
    try:
        existing = (
            db.query(Order)
            .filter((Order.order_id == order_id) | ((Order.u_id == u_id) & (Order.p_id == p_id)))
            .first()
        )
        if existing:
            return

        product = db.query(Product).filter(Product.id == p_id).first()
        if not product:
            raise ValueError("product not found")

        inventory = db.query(Inventory).filter(Inventory.p_id == p_id).with_for_update().first()
        if not inventory:
            raise ValueError("inventory not found")
        if inventory.available_stock < quantity:
            raise ValueError("insufficient db stock")

        inventory.available_stock -= quantity
        inventory.locked_stock += quantity

        order = Order(
            order_id=order_id,
            u_id=u_id,
            p_id=p_id,
            quantity=quantity,
            order_amount=order_amount,
            status=0,
        )
        db.add(order)
        db.commit()
    except Exception:
        db.rollback()
        redis_service.rollback_seckill_reservation(u_id=u_id, p_id=p_id, quantity=quantity)
        raise
    finally:
        db.close()


def _consume_loop() -> None:
    while not _stop_event.is_set():
        consumer = None
        try:
            consumer = KafkaConsumer(
                KAFKA_ORDER_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                enable_auto_commit=True,
                auto_offset_reset="earliest",
                consumer_timeout_ms=1000,
            )

            while not _stop_event.is_set():
                for message in consumer:
                    if _stop_event.is_set():
                        break
                    try:
                        process_order_message(message.value)
                    except Exception as exc:  # noqa: BLE001
                        logger.exception("Order consume failed: %s", exc)
                time.sleep(0.05)
        except KafkaError as exc:
            logger.error("Kafka consumer error: %s", exc)
            time.sleep(2)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Order consumer unexpected error: %s", exc)
            time.sleep(2)
        finally:
            if consumer is not None:
                consumer.close()


def start_order_consumer() -> None:
    global _consumer_thread

    if not KAFKA_ENABLED:
        logger.warning("Kafka disabled, order consumer not started")
        return

    if _consumer_thread is not None and _consumer_thread.is_alive():
        return

    _stop_event.clear()
    _consumer_thread = threading.Thread(target=_consume_loop, name="order-consumer", daemon=True)
    _consumer_thread.start()


def stop_order_consumer() -> None:
    global _producer

    _stop_event.set()

    if _producer is not None:
        try:
            _producer.close(timeout=5)
        finally:
            _producer = None
