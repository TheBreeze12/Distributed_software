from app.db.base import Base
from sqlalchemy import text, inspect
from app.db.session import engine, read_engine


def init_db():
    """
    初始化数据库（创建所有表）
    首次运行时调用此函数创建表结构
    """
    # 导入所有模型，确保它们被注册到Base.metadata
    # 注意：必须在函数内部导入，避免循环导入
    import app.models.user
    import app.models.product
    import app.models.order
    import app.models.inventory

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    ensure_order_schema()
    print("✅ 数据库表创建成功！")


def ensure_order_schema():
    inspector = inspect(engine)
    if "orders" not in inspector.get_table_names():
        return

    cols = {c["name"] for c in inspector.get_columns("orders")}
    with engine.begin() as conn:
        if "order_id" not in cols:
            conn.execute(text("ALTER TABLE orders ADD COLUMN order_id VARCHAR(32) NULL"))
            conn.execute(text("UPDATE orders SET order_id = CAST(id AS CHAR) WHERE order_id IS NULL"))
            conn.execute(text("ALTER TABLE orders MODIFY COLUMN order_id VARCHAR(32) NOT NULL"))

        uqs = {u["name"] for u in inspector.get_unique_constraints("orders")}
        if "uq_orders_order_id" not in uqs:
            try:
                conn.execute(text("ALTER TABLE orders ADD CONSTRAINT uq_orders_order_id UNIQUE (order_id)"))
            except Exception as e:
                print(f"⚠️  跳过 uq_orders_order_id 创建: {e}")
        if "uq_orders_user_product" not in uqs:
            try:
                conn.execute(text("ALTER TABLE orders ADD CONSTRAINT uq_orders_user_product UNIQUE (u_id, p_id)"))
            except Exception as e:
                print(f"⚠️  跳过 uq_orders_user_product 创建: {e}")



def check_db_connection():
    """
    检查数据库连接是否正常
    """
    try:
        with engine.connect() as conn:
            # SQLAlchemy 2.0 需要使用 text() 包装 SQL 语句
            conn.execute(text("SELECT 1"))
        with read_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库读写连接成功！")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False
