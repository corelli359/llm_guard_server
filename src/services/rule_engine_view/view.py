from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from tools.rule_engine_tools import InputRuleEngineTool
from sanic.request import Request
from models import SensitiveContext
from sanic.log import logger
from sanic_ext import validate
import time


class RuleEngineInputHandler(HTTPMethodView):
    @validate(json=SensitiveContext)
    async def post(self, request: Request, body: SensitiveContext) -> HTTPResponse:
        start = time.perf_counter_ns()
        tool = InputRuleEngineTool()
        tool.flow()
        await tool.execute(body)
        latency_ms = (time.perf_counter_ns() - start) / 1e6
        logger.info(f"【rule_engine】 {latency_ms:.2f} ms")

        # 将业务上下文挂到 request.ctx，审计中间件会自动采集
        request.ctx.sensitive_context = body.model_dump(mode="json")

        return json(
            {
                "final_decision": body.final_decision,
                "all_decision_dict": body.all_decision_dict,
            },
            200,
        )
        


