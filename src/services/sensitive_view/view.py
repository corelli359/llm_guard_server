from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from tools.sensitive_tools import SensitiveTool
from sanic.request import Request
from models import SensitiveContext
from sanic.log import logger
from sanic_ext import validate
import time

class SensitiveHandler(HTTPMethodView):
    @validate(json=SensitiveContext)
    async def post(self, request: Request, body: SensitiveContext) -> HTTPResponse:
        start = time.perf_counter_ns()
        tool = SensitiveTool()
        tool.flow()
        await tool.execute(body)
        latency_ms = (time.perf_counter_ns() - start) / 1e6
        logger.info(f"【sensitive】 {latency_ms:.2f} ms")

        request.ctx.sensitive_context = body.model_dump(mode="json")

        return json(body.final_result, 200)
