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
        # if body.use_vip_white and body.use_vip_black:
        #     raise Exception("VIP_WHITE_AND_WORDS_ALL_TRUE_ERROR")
        start = time.perf_counter_ns()
        tool = InputRuleEngineTool()
        tool.flow()
        await tool.execute(body)
        logger.info(f"【final】 {(time.perf_counter_ns() - start)/1e6} ms")
        
        return json(
            {
                # "senstive": body.final_result,
                # "guard": {"safety": body.safety, "category": body.category},
                "final_decision": body.final_decision,
                "all_decision_dict": body.all_decision_dict,
            },
            200,
        )
        


