from models import GuardResponse, GuardSafetyEnum, SensitiveContext, PassReasonEnum
from models import VllmType
from utils import LLMManager
from utils.error_codes import ErrorCode, ReturnCode
from sanic.log import logger
import time
from utils.logging_config import log_monitor


def content_parser(result):
    text = getattr(result, "content", result)
    if not text:
        logger.info("content_parser result is null")
        raise ValueError("empty guard model response")

    _dic = {}
    for line in str(text).strip().strip('"').splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        _dic[key.strip()] = value.strip()

    if "Categories" in _dic and "Category" not in _dic:
        _dic["Category"] = _dic["Categories"]
    if "Safety" in _dic:
        _dic["Safety"] = _dic["Safety"].upper()
    if _dic.get("Category", "").upper() in {"", "NONE", "NULL"}:
        _dic["Category"] = None
    return GuardResponse(**_dic)


class SafeGuardToolService:
    def __init__(self):
        self.llm = None
        self.parser = content_parser

    def _get_llm(self):
        if self.llm is None:
            self.llm = LLMManager.get_instance().get_model(VllmType.SAFE_MODEL)
        return self.llm

    def _build_messages(self, ctx: SensitiveContext):
        text = getattr(ctx, "input_text", "") or getattr(ctx, "input_prompt", "")
        if not ctx.is_output:
            return [("human", text)]

        question = getattr(ctx, "input_prompt", "") or text
        answer = getattr(ctx, "input_text", "") or text
        return [("human", question), ("ai", answer)]

    async def execute(
            self, ctx: SensitiveContext
    ) -> GuardResponse:
        cost_time = 0
        start_time = time.time()
        try:
            result = await self._get_llm().ainvoke(self._build_messages(ctx))
            logger.info(f"chain.ainvoke.result:{result}")
            parsed_result = self.parser(result)
            ctx.safety = parsed_result.Safety.value
            ctx.category = parsed_result.Category
            end_time = time.time()
            cost_time = end_time - start_time
            logger.info(f"safe guard tool execute cost time:{cost_time:.3f}s")
            log_monitor(
                traceid=ctx.request_id,
                app_id=ctx.app_id,
                trans_class="guard",
                version=ctx.versions,
                cost=cost_time,
                success=True,
                return_code=ReturnCode.SUCCESS[0]
            )
        except Exception as e:
            logger.exception(f"safe guard tool execute:{e}")
            logger.error(ErrorCode.AI_MODEL_SERVER_ERROR)
            log_monitor(
                traceid=ctx.request_id,
                app_id=ctx.app_id,
                trans_class="guard",
                version=ctx.versions,
                cost=cost_time,
                success=True,
                return_code=ReturnCode.GUARD_MODEL_EXCEPTION[0]
            )
            return GuardResponse(
                Safety=GuardSafetyEnum.SAFE,
                Category=None
            )
