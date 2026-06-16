from sanic import HTTPResponse, json
from sanic.views import HTTPMethodView
from tools.rule_engine_tools import InputRuleEngineTool
from sanic.request import Request
from models import SensitiveContext, AirRequestData
from sanic.log import logger
from sanic_ext import validate
import time
from utils.logging_config import log_monitor
import uuid
from utils.air_util import is_valid_rule_engine_air_params, make_result
from utils.error_codes import ReturnCode


class RuleEngineInputHandler(HTTPMethodView):
    @validate(json=SensitiveContext)
    async def post(self, request: Request, body: SensitiveContext) -> HTTPResponse:
        # if body.use_vip_white and body.use_vip_black:
        #     raise Exception("VIP_WHITE_AND_WORDS_ALL_TRUE_ERROR")
        body.request_ip = request.headers.get("x-real-ip")
        # logger.info(f"RuleEngineInputHandler request body: {body}")
        request_id = body.request_id
        input_text = body.input_prompt
        if not request_id:
            return json(
                {
                    "message": "request_id不能为空",
                    "errorCode": ReturnCode.INVALID_PARAM[0]

                },
                200,
            )
        if not input_text:
            return json(
                {
                    "message": "input_text不能为空",
                    "errorCode": ReturnCode.INVALID_PARAM[0]

                },
                200,
            )
        start = time.time()
        tool = InputRuleEngineTool()
        tool.flow()
        body.input_text = input_text
        body.use_customize_black = body.use_customize_black
        body.use_global_black = body.use_global_keywords
        await tool.execute(body)
        score = body.final_decision.get("score")
        result_dict = {
            0: "放行",
            100: "拒答"
        }
        logger.info(f"【final】 {time.time() - start:.3f} s")
        log_monitor(
            traceid=body.request_id,
            app_id=body.app_id,
            trans_class='RuleEngineInputHandler',
            cost=time.time() - start,
            success=True,
            return_code=ReturnCode.SUCCESS[0],
            version=body.versions
        )
        return json(
            {
                "score": score,  # 安全得分
                "result": result_dict.get(score),  # 得分结果
                "reason_detail": body.reason_detail,
                "reason": body.reason,  # 命中敏感词拒答的原因列表
                "data": body.words,  # 命中敏感词的数据列表
                "safety": body.safety,  # 大模型返回内容安全性结论
                "category": body.category,  # 大模型返回内容安全性分类
                "final_decision": body.final_decision,
                "all_decision_dict": body.all_decision_dict
            },
            200,
        )


class AirRuleEngineInputHandler(HTTPMethodView):
    @validate(json=AirRequestData)
    async def post(self, request: Request, body: AirRequestData) -> HTTPResponse:
        start = time.time()
        resp_id = str(uuid.uuid4())
        try:
            if not is_valid_rule_engine_air_params(body):
                return make_result(
                    body=body,
                    response_id=resp_id,
                    return_type=ReturnCode.INVALID_PARAM,
                )
            body.data.request_ip = request.headers.get("x-real-ip")
            body.data.app_id = body.data.api_key
            tool = InputRuleEngineTool()
            tool.flow()
            await tool.execute(body.data)
            score = body.data.final_decision.get("score")
            result_dict = {
                0: "放行",
                100: "拒答"
            }
            logger.info(f"【final】 {time.time() - start:.3f} s")
            log_monitor(
                traceid=body.data.request_id,
                app_id=body.data.app_id,
                trans_class='RuleEngineInputHandler',
                cost=time.time() - start,
                version=body.data.versions,
                success=True,
                return_code=ReturnCode.SUCCESS[0]
            )
            data = {
                "result": result_dict.get(score),  # 得分结果
                "reasonDetail": body.data.reason_detail,
                "score": score,  # 安全得分
                "sensitiveResult": {
                    "sensitiveTagLabels": body.data.reason,  # 命中敏感词拒答的原因列表
                    "sensitiveWords": body.data.words,  # 命中敏感词的数据列表
                },
                "decisionResult": {
                    "finalDecision": body.data.final_decision,
                    "riskRuleDetail": body.data.all_decision_dict,
                },
                "guardModelResult": {
                    "safety": body.data.safety,  # 大模型返回内容安全性结论
                    "category": body.data.category,  # 大模型返回内容安全性分类
                },
                "rewriteResult": {},
                "safetyAnswerResult": {}

            }
            return make_result(body=body, response_id=resp_id, return_type=ReturnCode.SUCCESS, data=data)
        except Exception as e:
            logger.info(f"RuleEngineInputHandler Air error:{e}")
            log_monitor(
                traceid=body.data.request_id,
                app_id=body.data.app_id,
                trans_class='RuleEngineInputHandler',
                cost=time.time() - start,
                success=False,
                version=body.data.versions,
                return_code=ReturnCode.INTERFACE_EXCEPTION[0]
            )
            return make_result(body=body, response_id=resp_id, return_type=ReturnCode.INTERFACE_EXCEPTION)
