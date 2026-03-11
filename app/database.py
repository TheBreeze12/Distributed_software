from app.db.base import Base
from sqlalchemy import text
from app.db.session import engine


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

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")



def check_db_connection():
    """
    检查数据库连接是否正常
    """
    try:
        with engine.connect() as conn:
            # SQLAlchemy 2.0 需要使用 text() 包装 SQL 语句
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功！")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False
