from enum import StrEnum

from pydantic import BaseModel, Field


class SafetyRewriteResult(BaseModel):
    user_intent: str = Field(description="清洗后的用户核心意图")
    rewritten_text: str = Field(
        description="基于TC260无害化改写后的文本，若无法改写则为空"
    )
    is_safe_now: bool = Field(description="改写后是否安全可用")
    hit_rule: str | None = Field(
        description="触发的TC260规则编号，如 A.2.20，无触发则为 null"
    )
    rewrite_decision: int = 50


class GuardSafetyEnum(StrEnum):
    SAFE = "safe".upper()
    UNSAFE = "unsafe".upper()
    CONTROVERSIAL = "controversial".upper()


class GuardCategoryEnum(StrEnum):
    VIOLENT = "violent"
    ILLEGAL_NON_VIOLENT = "illegal_non_violent"
    SEXUAL = "sexual"
    PII = "pii"
    SELF_HARM = "self_harm"
    UNETHICAL = "unethical"
    POLITICAL = "political"
    COPYRIGHT = "copyright"
    JAILBREAK = "jailbreak"


class GuardResponse(BaseModel):
    Safety: GuardSafetyEnum = Field(..., description="安全等级")
    Category: str | None = Field(default=None, description="风险类别")
    # Category: GuardCategoryEnum | None = Field(default=None, description="风险类别")


class PassReasonEnum(StrEnum):
    CONTENT_SAFETY = "内容安全"
    SUPER_WHITELIST_BYPASS = "超白放行"
    DEFAULT_PASS = "未配置规则放行"
    AI_MODEL_EXCEPTION = "模型服务未响应默认放行"


class RejectReasonEnum(StrEnum):
    SENSITIVE_WORD_HIT = "命中敏感词"
    CONTENT_UNSAFETY = "内容不安全且命中规则"
    SUPER_BLACKLIST_REJECT = "超黑拒绝"
