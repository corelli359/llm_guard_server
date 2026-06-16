import time
from enum import IntEnum
from typing import Any, Dict
from mock_api.mock_llm import GuardSafetyEnum
from models import SensitiveContext, DecisionClassifyEnum, PassReasonEnum, RejectReasonEnum
from sanic.log import logger
from ..data_tool.data_provider import DataProvider
import traceback
from utils.logging_config import log_monitor, desensitize_msg
from utils.error_codes import ReturnCode


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
    if ctx.use_customize_black and custom:
        use_customize = True
    if ctx.final_result:
        for k, v in ctx.final_result.items():
            _label = f"{k}-{ctx.safety}"
            if _label not in data_provider.global_rules:
                logger.error(f"KEY_NOT_IN_RULE_ERROR -- {_label}")
                raise Exception("KEY_NOT_IN_RULE_ERROR")
            else:
                # decision = RULE_DICT_MOCK[_label]
                decision = data_provider.global_rules[_label]
                if use_customize:
                    if _label in customize_rule:
                        decision = DecisionClassifyEnum(customize_rule.get(_label))

                if decision.value > final_decision:
                    final_decision = decision.value
                    decision_dict = {k: v}
                decision_details[_label] = {"decision": decision.value, "words": v}
        return decision.value, decision_dict, decision_details
    else:
        if not ctx.safety:
            ctx.reason_detail = PassReasonEnum.AI_MODEL_EXCEPTION
            return -1, {}, {}

        _label = f"-{ctx.safety}"
        # 查询是否存在空tag_code的规则
        if _label not in data_provider.global_rules:
            logger.info(f"没有配置空tag_code规则，默认放行:{_label}, {ctx.input_text}")
            if ctx.reason_detail is None:
                ctx.reason_detail = PassReasonEnum.DEFAULT_PASS
            return -1, {}, {}
        if ctx.reason_detail is None:
            ctx.reason_detail = RejectReasonEnum.CONTENT_UNSAFETY
        decision = data_provider.global_rules[_label]
        decision_dict = {_label: {"decision": decision.value, "words": []}}
        return decision.value, decision_dict, decision_dict


async def make_decision(ctx: SensitiveContext):
    start = time.time()
    final_decision_dict = {"score": -1, "priority": -1}

    decision_details: Dict[str, Dict[str, Any]] = {}
    decision_dict = {}

    data_provider: DataProvider = DataProvider.get_instance()
    # custom = data_provider.custom_ac.get(ctx.app_id)
    custom_vip = data_provider.custom_vip.get(ctx.app_id)

    if ctx.safety == GuardSafetyEnum.SAFE:
        ctx.reason_detail = PassReasonEnum.CONTENT_SAFETY

    def decision_jugde(_decision, priority):
        nonlocal final_decision_dict
        if final_decision_dict["score"] < 0 and _decision > -1:
            final_decision_dict["score"] = _decision
            final_decision_dict["priority"] = priority
        elif final_decision_dict["score"] > -1 and _decision > -1:
            if priority > final_decision_dict["priority"]:
                final_decision_dict["score"] = _decision

    try:
        if ctx.use_vip_black and ctx.vip_black_words_result:
            value = DecisionSource.VIP_BLACK_WORDS.value
            _final_decision = rank_by_words(DecisionClassifyEnum.REJECT)
            decision_jugde(_final_decision, value)
            decision_details[str(value)] = ctx.vip_black_words_result
            ctx.reason_detail = RejectReasonEnum.SUPER_BLACKLIST_REJECT

        if ctx.use_vip_white and ctx.vip_white_words_result:
            value = DecisionSource.VIP_WHITE_WORDS.value
            _final_decision = rank_by_words(DecisionClassifyEnum.PASS)
            decision_jugde(_final_decision, value)
            decision_details[str(value)] = ctx.vip_white_words_result
            ctx.reason_detail = PassReasonEnum.SUPER_WHITELIST_BYPASS

        value = DecisionSource.NORMAL_RULE.value
        _final_decision, _data, _details = await rank_by_normal_rules(ctx)
        if _final_decision != -1:
            decision_jugde(_final_decision, DecisionSource.NORMAL_RULE)
            decision_details[str(value)] = _details
            decision_dict = _data
        # if ctx.use_vip_black and CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT.get(ctx.app_id, {}):
        if ctx.use_vip_black and custom_vip and custom_vip.black_rule:
            value = DecisionSource.VIP_BLACK_RULE.value
            _final_decision, _details = rank_by_vip_rules(ctx, custom_vip.black_rule)
            decision_jugde(_final_decision, value)
            decision_details[str(value)] = _details
            ctx.reason_detail = RejectReasonEnum.SUPER_BLACKLIST_REJECT

        # if ctx.use_vip_white and CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT.get(ctx.app_id, {}):
        if ctx.use_vip_white and custom_vip and custom_vip.white_rule:
            value = DecisionSource.VIP_WHITE_RULE.value
            _final_decision, _details = rank_by_vip_rules(ctx, custom_vip.white_rule)
            decision_jugde(_final_decision, value)
            decision_details[str(value)] = _details
            ctx.reason_detail = PassReasonEnum.SUPER_WHITELIST_BYPASS

        if final_decision_dict["score"] < 0:
            final_decision_dict["score"] = DecisionClassifyEnum.PASS.value
    except Exception as e:
        log_monitor(
            traceid=ctx.request_id,
            app_id=ctx.app_id,
            trans_class="make_decision",
            cost=time.time() - start,
            success=True,
            version=ctx.versions,
            return_code=ReturnCode.DECISION_EXCEPTION[0]
        )
        logger.error(f"decision_jugde error :{e}")
        traceback.print_exc()
    ctx.final_decision = final_decision_dict
    if ctx.reason_detail is None:
        if final_decision_dict.get("score") == 100:
            ctx.reason_detail = RejectReasonEnum.SENSITIVE_WORD_HIT

        if final_decision_dict.get("score") == 0:
            ctx.reason_detail = PassReasonEnum.CONTENT_SAFETY

    ctx.all_decision_dict = decision_details
    ctx.decision_dict = decision_dict
    words = []
    reason = []
    meta_tags_dict = data_provider.meta_tags_dict
    for score, v in decision_details.items():
        for tag_code, x in v.items():
            if isinstance(x, dict):  # 过滤超黑超白
                if x.get("words"):
                    words += x["words"]
                tag_co = tag_code.split('-')[0]
                rea = meta_tags_dict.get(tag_co)
                if rea:
                    reason.append(rea)

    ctx.words = words
    ctx.reason = reason
    logger.info(f"【make_decision】 {time.time() - start:.3f} s")
    log_monitor(
        traceid=ctx.request_id,
        app_id=ctx.app_id,
        trans_class="make_decision",
        cost=time.time() - start,
        success=True,
        version=ctx.versions,
        return_code=ReturnCode.DECISION_RULE_NOT_FOUND[0] if ctx.reason_detail == PassReasonEnum.DEFAULT_PASS else
        ReturnCode.SUCCESS[0]
    )
    record = {
        "scenario_id": ctx.app_id,
        "input_text": desensitize_msg(ctx.input_text)[0:511],
        "keywords": f"{ctx.words}",
        "safety": ctx.safety,
        "result": "放行" if ctx.final_decision['score'] == 0 else "拒答",
        "score": ctx.final_decision["score"],
        "priority": ctx.final_decision["priority"],
        "category": ctx.category,
        "reason": f'{ctx.reason}',
        "request_id": ctx.request_id
    }
    await data_provider.save_log_record(record)
