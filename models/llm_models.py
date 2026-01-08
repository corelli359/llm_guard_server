import os
from enum import Enum, IntEnum

#  TODO 模型版本


class VllmType(str, Enum):

    SAFE_MODEL = "deepseek_chat"  # 后面可以改成safeguard


class DecisionClassifyEnum(IntEnum):
    PASS = 0
    REJECT = 100
    REWRITE = 50
    MANUAL = 1000


DECISION_MAPPING: dict = {
    "BLOCK": DecisionClassifyEnum.REJECT,
    "PASS": DecisionClassifyEnum.PASS,
    "REWRITE": DecisionClassifyEnum.REWRITE,
    "REVIEW": DecisionClassifyEnum.MANUAL,
}
