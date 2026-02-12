from enum import IntEnum
from typing import Any, Dict
from mock_api.mock_llm import GuardSafetyEnum
from models import SensitiveContext, DecisionClassifyEnum
from sanic.log import logger
from ..data_tool.data_provider import DataProvider


class DecisionSource(IntEnum):
    NORMAL_RULE = 100
    VIP_WHITE_RULE = 700
    VIP_BLACK_RULE = 800
    VIP_WHITE_WORDS = 900
    VIP_BLACK_WORDS = 1000


def rank_by_words(action: DecisionClassifyEnum):
    final_decision: int = action.value
    return final_decision


def rank_by_vip_rules(ctx: SensitiveContext, rule_dict: dict):
    final_decision: int = -1
    decision_dict: dict = {}
    for label, V in ctx.final_result.items():
        if label in rule_dict:
            decision: DecisionClassifyEnum = rule_dict[label]
            if decision.value > final_decision:
                final_decision = decision.value
                decision_dict = {label: V}
    return final_decision, decision_dict


async def rank_by_normal_rules(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()
    final_decision: int = -1
    use_customize: bool = False
    customize_rule: dict = {}
    decision_dict: dict = {}
    decision_details: Dict[str, Dict[str, Any]] = {}
    decision: DecisionClassifyEnum = DecisionClassifyEnum.PASS
    custom = data_provider.custom_ac.get(ctx.app_id, None)
    if ctx.use_customize_rule and custom:
        if data_provider.custom_ac[ctx.app_id]:
            if custom.custom_rule:
                customize_rule = custom.custom_rule
        if customize_rule:
            use_customize = True
    for k, v in ctx.final_result.items():
        _label = f"{k}-{ctx.safety}"

        if not data_provider.global_rules.get(_label):
            logger.error(f"KEY_NOT_IN_RULE_ERROR -- {_label}")
            raise Exception("KEY_NOT_IN_RULE_ERROR")
        else:
            # decision = RULE_DICT_MOCK[_label]
            decision = data_provider.global_rules[_label]
            if use_customize and _label in customize_rule:
                decision = DecisionClassifyEnum(customize_rule.get(_label))
            if decision.value > final_decision:
                final_decision = decision.value
                decision_dict = {k: v}
            decision_details[_label] = {"decision": decision.value, "words": v}
    return decision.value, decision_dict, decision_details


async def make_decision(ctx: SensitiveContext):

    final_decision_dict = {"score": -1, "priority": -1}

    decision_details: Dict[str, Dict[str, Any]] = {}
    decision_dict = {}

    data_provider: DataProvider = DataProvider.get_instance()
    # custom = data_provider.custom_ac.get(ctx.app_id)
    custom_vip = data_provider.custom_vip.get(ctx.app_id)

    def decision_jugde(_decision, priority):
        nonlocal final_decision_dict
        if final_decision_dict["score"] < 0 and _decision > -1:
            final_decision_dict["score"] = _decision
            final_decision_dict["priority"] = priority
        elif final_decision_dict["score"] > -1 and _decision > -1:
            if priority > final_decision_dict["priority"]:
                final_decision_dict["score"] = _decision

    if ctx.use_vip_black and ctx.vip_black_words_result:
        value = DecisionSource.VIP_BLACK_WORDS.value
        _final_decision = rank_by_words(DecisionClassifyEnum.REJECT)
        decision_jugde(_final_decision, value)
        decision_details[str(value)] = ctx.vip_black_words_result

    if ctx.use_vip_white and ctx.vip_white_words_result:
        value = DecisionSource.VIP_WHITE_WORDS.value
        _final_decision = rank_by_words(DecisionClassifyEnum.PASS)
        decision_jugde(_final_decision, value)
        decision_details[str(value)] = ctx.vip_white_words_result

    if ctx.final_result:
        value = DecisionSource.NORMAL_RULE.value
        _final_decision, _data, _details = await rank_by_normal_rules(ctx)
        decision_jugde(_final_decision, DecisionSource.NORMAL_RULE)
        decision_details[str(value)] = _details
        decision_dict = _data

    # if ctx.use_vip_black and CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT.get(ctx.app_id, {}):
    if ctx.use_vip_black and custom_vip and custom_vip.black_rule:
        value = DecisionSource.VIP_BLACK_RULE.value
        _final_decision, _details = rank_by_vip_rules(ctx, custom_vip.black_rule)
        decision_jugde(_final_decision, value)
        decision_details[str(value)] = _details

    # if ctx.use_vip_white and CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT.get(ctx.app_id, {}):
    if ctx.use_vip_white and custom_vip and custom_vip.white_rule:
        value = DecisionSource.VIP_WHITE_RULE.value
        _final_decision, _details = rank_by_vip_rules(ctx, custom_vip.white_rule)
        decision_jugde(_final_decision, value)
        decision_details[str(value)] = _details

    if final_decision_dict["score"] < 0:
        final_decision_dict["score"] = DecisionClassifyEnum.PASS.value
    ctx.final_decision = final_decision_dict
    ctx.all_decision_dict = decision_details
    ctx.decision_dict = decision_dict
