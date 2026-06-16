from typing import Dict, Any, List, Set
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel, to_snake


class SensitivePromiseInput(BaseModel):
    request_id: str = Field(default="", min_length=1, description="请求ID")
    request_ip: str = Field(default="", description="请求ip")
    app_id: str = Field(default="",description="app_id")
    api_key: str = Field(default="", description="场景id")
    versions: str = Field(default="", description="版本")
    input_text: str = Field(default="", min_length=1, description="用户输入")
    input_prompt: str = Field(default="", min_length=1, description="用户输入")
    is_output: bool = False
    use_customize_white: bool = False
    use_customize_black: bool = False
    use_customize_words: bool = False
    use_customize_rule: bool = False
    use_vip_black: bool = False
    use_vip_white: bool = False
    use_global_black: bool = True  # 是否使用全局敏感词兜底 默认兜底
    use_global_keywords: bool = True
    exemption_distance: int = 0
    use_safety_answer: bool = False  # 是否使用代答
    use_rewrite: bool = False  # 是否使用意图识别

    # @field_validator('apikey')
    # @classmethod
    # def validate_apikey(cls, v: str):
    #     if not v.startswith("sk-"):
    #         raise ValueError("Invalid API Key format, must start with 'sk-'")
    #     return v


class SensitiveData(BaseModel):
    # result: Dict[str, Any] = Field(default_factory=dict)
    customize_result: Dict[str, List] = Field(default_factory=dict)
    vip_black_words_result: Dict[str, List] = Field(default_factory=dict)
    vip_white_words_result: Dict[str, List] = Field(default_factory=dict)
    global_result: Dict[str, List] = Field(default_factory=dict)
    final_result: Dict[str, List] = Field(default_factory=dict)
    original_input_text: str | None = None
    exemption_set: Set[str] = Field(default_factory=set)


class GuardData(BaseModel):
    safety: str = Field(default="")
    category: str | None = Field(default=None)


class DecisionData(BaseModel):
    final_decision: Dict[str, Any] = Field(default_factory=dict)
    decision_dict: Dict[str, Any] = Field(default_factory=dict)
    all_decision_dict: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    rewrite_result: Dict[str, Any] = Field(default_factory=dict)
    reason: List[str] = Field(default_factory=list)
    words: List[str] = Field(default_factory=list)
    safety: str = Field(default="")
    category: str | None = Field(default=None)
    reason_detail: str | None = Field(default=None)


class SensitiveContext(SensitivePromiseInput, SensitiveData, GuardData, DecisionData):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore"
    )


class ReloadDataContext(BaseModel):
    app_id: str = Field(default="",description="app_id")
    reload_global: bool = False
    reload_customize: bool = False
    reload_vip: bool = False


class AirRequestData(BaseModel):
    appId: str = Field(..., description="appId")
    trCode: str = Field(..., description="trCode")
    trToken: str = Field(..., description="trToken")
    trVersion: str = Field(..., description="trVersion")
    requestId: str = Field(..., description="requestId")
    timestamp: str = Field(..., description="timestamp")
    data: SensitiveContext
