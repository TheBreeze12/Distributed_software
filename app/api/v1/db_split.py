from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.deps import get_db_read, get_db_write

router = APIRouter(prefix="/api/v1/db-split", tags=["db-split"])


@router.get("/read-info")
def read_info(db=Depends(get_db_read)):
    row = db.execute(
        text("SELECT @@hostname AS host, @@server_id AS server_id, @@read_only AS read_only")
    ).mappings().first()
    return {
        "role": "read",
        "host": row["host"],
        "server_id": int(row["server_id"]),
        "read_only": int(row["read_only"]),
    }


@router.get("/write-info")
def write_info(db=Depends(get_db_write)):
    row = db.execute(
        text("SELECT @@hostname AS host, @@server_id AS server_id, @@read_only AS read_only")
    ).mappings().first()
    return {
        "role": "write",
        "host": row["host"],
        "server_id": int(row["server_id"]),
        "read_only": int(row["read_only"]),
    }


@router.post("/replication-test")
def replication_test(db_write=Depends(get_db_write), db_read=Depends(get_db_read)):
    db_write.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS rw_split_test (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                marker VARCHAR(128) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """
        )
    )
    marker = f"marker-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    db_write.execute(text("INSERT INTO rw_split_test(marker) VALUES (:marker)"), {"marker": marker})
    db_write.commit()

    write_count = db_write.execute(
        text("SELECT COUNT(*) AS cnt FROM rw_split_test WHERE marker = :marker"), {"marker": marker}
    ).scalar_one()

    read_count = db_read.execute(
        text("SELECT COUNT(*) AS cnt FROM rw_split_test WHERE marker = :marker"), {"marker": marker}
    ).scalar_one()

    return {
        "marker": marker,
        "write_count": int(write_count),
        "read_count": int(read_count),
        "replication_ok": int(read_count) >= 1,
        "note": "若 read_count=0，通常是主从复制延迟，请稍后重试。",
    }
