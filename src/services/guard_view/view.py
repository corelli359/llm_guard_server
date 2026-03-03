
from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from tools.guard_tools import GuardTool
from sanic.request import Request
from models import SensitiveContext
from sanic.log import logger
from sanic_ext import validate
import time


class GuardHandler(HTTPMethodView):
    @validate(json=SensitiveContext)
    async def post(self, request: Request, body: SensitiveContext) -> HTTPResponse:
        start = time.perf_counter_ns()
        tool = GuardTool()
        tool.flow()
        await tool.execute(body)
        latency_ms = (time.perf_counter_ns() - start) / 1e6
        logger.info(f"【guard】 {latency_ms:.2f} ms")

        request.ctx.sensitive_context = body.model_dump(mode="json")

        return json({"Safety": body.safety, "Category": body.category}, 200)
