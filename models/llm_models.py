import os
from enum import Enum

#  TODO 模型版本

class VllmType(str, Enum):
    
    SAFE_MODEL = "deepseek_chat"   # 后面可以改成safeguard
    
      