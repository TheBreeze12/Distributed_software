from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from app.api.v1 import user,product,order
from contextlib import asynccontextmanager
from app.database import check_db_connection,init_db

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

    yield  # 应用运行期间

    # 关闭时执行（如果需要清理资源，在这里添加）
    print("🛑 应用关闭中...")


app=FastAPI(title="智能生活服务工具API",
    description="提供餐饮营养分析、出行规划等AI驱动的生活服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # 使用新的lifespan事件处理器
)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(order.router)
@app.get("/")
def get_root():
    return{
        "hello":"world"
    }

if __name__=="__main__":
    print("系统启动")
