from utils.execute_utils import run_in_async
from utils import Promise, async_perf_count
from models import SensitiveContext
from ..guard_tools import GuardTool
from ..sensitive_tools import SensitiveTool
from .decision_maker import make_decision
from ..intent_tools import IntentService
from models import SafetyRewriteResult
from ..string_filter_tools import remove_control_chars
from ..data_tool.data_provider import DataProvider


async def custom_vip_load_by_db(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()
    custom_vip = data_provider.custom_vip.get(ctx.app_id)
    if not custom_vip or not custom_vip.loaded:
        await data_provider.build_ac("vip", ctx.app_id)


async def rewrite_chat(ctx: SensitiveContext):
    """
    Docstring for rewrite_chat
    1、清洗敏感词数据
    2、大模型对话
    3、检查
    4、赋值
    :param ctx: Description
    :type ctx: SensitiveContext
    """
    all_words: list = [
        data
        for v1 in ctx.all_decision_dict.values()
        for v2 in v1.values()
        for data in v2.get("words", [])
    ]
    intent_instance: IntentService = IntentService()
    res: SafetyRewriteResult = await intent_instance.execute(
        ctx.input_prompt, all_words
    )
    if not res.is_safe_now:
        res.rewrite_decision = 100
    ctx.rewrite_result = res.model_dump()


async def do_action_by_decision(ctx: SensitiveContext):
    score: int = ctx.final_decision.get("score", -1)
    match score:
        case 0 | 100 | 1000:
            pass
        case 50:
            await rewrite_chat(ctx)
        case _:
            raise Exception("NO_DECISION_FOUND_ERROR")


class RuleEngineTool:
    def __init__(self) -> None:
        self.promise = Promise()

    def flow(self):
        guard_tool = GuardTool()
        sensitive_tool = SensitiveTool()
        guard_tool.flow()
        sensitive_tool.flow()
        self.promise.then(
            remove_control_chars,
            custom_vip_load_by_db,
            # customize_vip_white_rule_load,
            # customize_vip_black_rule_load,
        ).then(sensitive_tool.execute, guard_tool.execute).then(make_decision).then(
            do_action_by_decision
        )

    @async_perf_count
    async def execute(self, ctx: SensitiveContext):
        await self.promise.execute(ctx)
