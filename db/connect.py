import select
from sanic import Sanic
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from sqlalchemy import select
from sanic.log import logger
from sympy import N

# AsyncSessionFactory = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,  # 指定使用异步 Session 类
#     expire_on_commit=False,  # 防止提交后属性过期导致额外的 SQL 查询
#     autoflush=False,  # (可选) 建议在异步高并发场景关闭自动 flush
#     autocommit=False,  # (可选) 现在的版本通常默认为 False
# )


class DBConnector:
    conn: AsyncEngine
    app: Sanic
    db_url: str = DATABASE_URL

    async def ping(self):
        try:
            async with self.conn.connect() as conn:
                await conn.scalar(select(1))
                logger.info(f"mysql connected!")
        except Exception as e:
            logger.error(f"mysql connect failed {str(e)} ")

    def init_db(self, app: Sanic, **kwargs):
        self.app = app

        @app.after_server_start
        async def aio_mysql_start(_app: Sanic, _loop):
            self.conn = create_async_engine(
                self.db_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            )
            await self.ping()

        @app.after_server_stop
        async def close(_app: Sanic, _loop):
            await self.conn.dispose()
