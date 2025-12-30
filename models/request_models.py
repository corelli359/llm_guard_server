from typing import Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class SensitivePromiseInput(BaseModel):
    request_id: str = Field(..., min_length=1, description="请求ID")
    app_id: str = Field(..., min_length=3, max_length=20)
    apikey: str = Field(..., description="密钥")
    input_prompt: str = Field(..., min_length=1, description="用户输入")
    use_customize_white: bool = False
    use_customize_words: bool = False
    use_customize_rule: bool = False
    use_vip_black: bool = False
    use_vip_white: bool = False

    # @field_validator('apikey')
    # @classmethod
    # def validate_apikey(cls, v: str):
    #     if not v.startswith("sk-"):
    #         raise ValueError("Invalid API Key format, must start with 'sk-'")
    #     return v


class SensitiveData(BaseModel):
    result: Dict[str, Any] = Field(default_factory=dict)
    customize_result: Dict[str, List] = Field(default_factory=dict)
    vip_black_words_result: Dict[str, List] = Field(default_factory=dict)
    vip_white_words_result: Dict[str, List] = Field(default_factory=dict)
    global_result: Dict[str, List] = Field(default_factory=dict)
    final_result: Dict[str, List] = Field(default_factory=dict)


class GuardData(BaseModel):
    safety: str = Field(default="")
    category: str | None = Field(default=None)


class DecisionData(BaseModel):
    final_decision: Dict[str, Any] = Field(default_factory=dict)
    decision_dict: Dict[str, Any] = Field(default_factory=dict)
    all_decision_dict: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class SensitiveContext(SensitivePromiseInput, SensitiveData, GuardData, DecisionData):
    model_config = ConfigDict(extra="ignore")
