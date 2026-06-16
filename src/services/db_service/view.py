from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.log import logger
from sanic_ext import validate
import time
from tools.db_tools import DBConnectTool
from tools.data_tool import DataProvider, DataInitPromise
from models.request_models import ReloadDataContext
from utils import run_in_async


class DBHandle(HTTPMethodView):

    def __init__(self, db_tool: DBConnectTool) -> None:
        self.db_tool = db_tool

    async def get(self, request: Request) -> HTTPResponse:
        start = time.perf_counter_ns()

        result = await self.db_tool.load_data_from_db()
        logger.info(f"【1】 {(time.perf_counter_ns() - start) / 1e6} ms")

        return json({"data_count": len(result['global_keywords'])}, 200)


class ReloadDataView(HTTPMethodView):
    @validate(json=ReloadDataContext)
    async def post(self, request: Request, body: ReloadDataContext) -> HTTPResponse:
        """
        POST /api/data/reload
        :param request:
        :return:
        """
        try:
            logger.info("Loading data from DB...")
            db_tool = request.app.ctx.db_tool
            logger.info(request.app.ctx)
            if db_tool is None:
                return json({
                    "code": 500,
                    "message": "数据库工具未初始化"
                }, 500)

            if not  body.app_id and not body.reload_global:
                return json({
                    "code": 500,
                    "message": "参数未给，无需reload"
                })
            start_time = time.perf_counter_ns()
            data_provider: DataProvider = DataProvider.get_instance()
            if body.app_id:
                if body.reload_vip:
                    await data_provider.update_vip(body.app_id)  # shao black ac white ac rule
                    logger.info(f"{body.app_id}场景更新超级敏感词成功")
                if body.reload_customize:
                    await data_provider.update_customize(body.app_id)  # 比之前多
                    logger.info(f"{body.app_id}场景更新自定义敏感词成功")
            if body.reload_global:
                # 更新全局敏感词
                await DataInitPromise().reload_global_data(data_provider)
            elapsed_ms = (time.perf_counter_ns() - start_time) / 1e6

            logger.info(f"Data reloaded successfully in {elapsed_ms:.2f}ms")
            return json({
                "code": 200,
                "message": "数据重新加载成功",
                "data": {
                    "elapsed_time_ms": elapsed_ms,
                }
            }, 200)

        except Exception as e:
            logger.error(f"Failed to load data from DB: {e}")
            return json({
                "code": 500,
                "message": f"数据重新加载失败:{e}"
            }, 500)
