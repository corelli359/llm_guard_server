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
