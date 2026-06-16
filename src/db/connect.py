from sanic import Sanic
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
)
import os
from sqlalchemy import select
from sanic.log import logger


class DBConnector:
    conn: AsyncEngine
    app: Sanic
    db_url: str = os.getenv("DATABASE_URL", "")

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
        async def aio_mysql_start(_app: Sanic):
            if not self.db_url:
                raise RuntimeError("DATABASE_URL is required when DATA_SOURCE_MODE=DB")
            self.conn = create_async_engine(
                self.db_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
            )
            await self.ping()

        @app.after_server_stop
        async def close(_app: Sanic):
            await self.conn.dispose()
