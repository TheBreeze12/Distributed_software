from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from app.api.v1 import user,product,order,inventory,db_split
from contextlib import asynccontextmanager
from app.database import check_db_connection,init_db
from app.core.redis_client import redis_client
from app.api.deps import get_db
from app.db.session import SessionLocal
from app.services import redis_service
from app.services import kafka_order_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理（启动和关闭事件）
    替代已弃用的 @app.on_event("startup") 和 @app.on_event("shutdown")
    """
    # 启动时执行
    print("🚀 应用启动中...")
    # 检查数据库连接
    if check_db_connection():
        print("✅ 数据库连接正常")
        # 自动初始化数据库表（如果不存在则创建，已存在则跳过）
        try:
            init_db()
            print("✅ 数据库表初始化完成")
        except Exception as e:
            print(f"⚠️  数据库表初始化警告: {e}")
    else:
        print("⚠️  警告：数据库连接失败，请检查配置")

    try:
        redis_client.ping()
        print("Redis连接正常")
    except Exception as e:
        print("Redis连接失败"+str(e))

    try:
        db=SessionLocal()
        count=redis_service.warm_up_stock_to_redis(db)
        print("库存预热成功"+str(count)+"件")
        count=redis_service.warm_up_product_to_redis(db)
        print("商品预热成功"+str(count)+"件")
    except Exception as e:
        print("库存预热失败"+str(e))
    finally:
        db.close()

    try:
        kafka_order_service.start_order_consumer()
        print("Kafka订单消费者已启动")
    except Exception as e:
        print("Kafka消费者启动失败"+str(e))

    yield  # 应用运行期间

    # 关闭时执行（如果需要清理资源，在这里添加）
    kafka_order_service.stop_order_consumer()
    print("🛑 应用关闭中...")


app=FastAPI(title="秒杀商城后端API",
    description="这是一个使用FastAPI构建的秒杀商城后端API，提供用户注册、登录、商品浏览、下单等功能。",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # 使用新的lifespan事件处理器
)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(inventory.router)
app.include_router(db_split.router)
@app.get("/")
def get_root():
    return{
        "hello":"world"
    }

if __name__=="__main__":
    print("系统启动")
