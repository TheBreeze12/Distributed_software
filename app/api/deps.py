from collections.abc import Generator
from app.db.session import ReadSessionLocal, WriteSessionLocal


def get_db_write() -> Generator:
    db = WriteSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_read() -> Generator:
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Backward compatibility: default dependency keeps old symbol name.
def get_db() -> Generator:
    yield from get_db_write()
