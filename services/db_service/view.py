from codecs import lookup
from turtle import st
from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.log import logger
from sanic_ext import validate
import time
from tools.db_tools import DBConnectTool


class DBHandle(HTTPMethodView):

    def __init__(self, db_tool: DBConnectTool) -> None:
        self.db_tool = db_tool

    async def get(self, request: Request) -> HTTPResponse:
        start = time.perf_counter_ns()

        result = await self.db_tool.load_data_from_db()
        logger.info(f"【1】 {(time.perf_counter_ns() - start)/1e6} ms")
        
        return json({"data_count": len(result['global_keywords'])}, 200)
