from calendar import c
from utils.execute_utils import run_in_async
from utils import Promise, async_perf_count
from models import SensitiveContext
from ..guard_tools import GuardTool
from ..sensitive_tools import SensitiveTool
from .decision_maker import make_decision
from config import (
    CUSTOMIZE_RULE_VIP_BLACK_RULE_PATH,
    CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT,
    CUSTOMIZE_RULE_VIP_WHITE_RULE_PATH,
    CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT,
)


def load_rule(app_id: str, path: dict, mapping: dict, flush: bool = False):
    if flush or app_id not in mapping:
        __path: str | None = mapping.get(app_id)
        rule_list : list | None = None
        if __path:
            with open(__path, "r") as f:
                rule_list = f.readlines()
            rule_list = [_.strip() for _ in rule_list]
        else:
            rule_list = None

        mapping[app_id] = {"loaded": True, "data": rule_list}


async def customize_vip_white_rule_load(ctx: SensitiveContext):
    if ctx.use_vip_white and CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT.get(ctx.app_id):
        await run_in_async(
            load_rule,
            ctx.app_id,
            CUSTOMIZE_RULE_VIP_WHITE_RULE_PATH,
            CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT,
        )


async def customize_vip_black_rule_load(ctx: SensitiveContext):
    if ctx.use_vip_black and CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT.get(ctx.app_id):
        await run_in_async(
            load_rule,
            ctx.app_id,
            CUSTOMIZE_RULE_VIP_BLACK_RULE_PATH,
            CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT,
        )


class RuleEngineTool:
    def __init__(self) -> None:
        self.promise = Promise()

    def flow(self):
        guard_tool = GuardTool()
        sensitive_tool = SensitiveTool()
        guard_tool.flow()
        sensitive_tool.flow()
        self.promise.then(
            customize_vip_white_rule_load, customize_vip_black_rule_load
        ).then(sensitive_tool.execute, guard_tool.execute).then(make_decision)

    @async_perf_count
    async def execute(self, ctx: SensitiveContext):
        await self.promise.execute(ctx)
