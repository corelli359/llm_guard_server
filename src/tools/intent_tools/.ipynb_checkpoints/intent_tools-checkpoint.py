from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils import LLMManager
from models import VllmType, SafetyRewriteResult


from langchain_core.prompts import ChatPromptTemplate

from .intent_prompt_template import TC260_REWRITE_PROMPT
from config import DEEP_SEEK_API_KEY

API_KEY: str | None = DEEP_SEEK_API_KEY

# api_key_path = "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/data/deepseek_apikey.txt"
# with open(api_key_path, "r") as f:
#     API_KEY = f.read().strip()

if not API_KEY:
    raise Exception("NO_APIKEY_ERROR")


# ==========================================
# 2. 意图识别与改写服务
# ==========================================
class IntentService:
    def __init__(self):
        """
        初始化服务：
        1. 获取 LLM 实例（从单例管理器）
        2. 配置 Prompt 模板
        3. 配置 Pydantic 解析器
        """
        # 从单例池获取 DeepSeek (响应速度快，适合意图识别)
        self.llm = LLMManager.get_instance().get_model(VllmType.SAFE_MODEL)

        self.parser = PydanticOutputParser(pydantic_object=SafetyRewriteResult)

        # 构建 Prompt
        # system 消息使用我们定义的 TC260_REWRITE_PROMPT
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", TC260_REWRITE_PROMPT),
                # 将上游检测到的敏感词传入，辅助大模型判断
                (
                    "human",
                    "【系统检测到的敏感词】: {triggered_keywords}\n【用户原始内容】: {user_input}",
                ),
            ]
        )

        # 预编译 Chain (Prompt | LLM | Parser)
        self.chain = self.prompt_template | self.llm | self.parser

    async def execute(
        self, text: str, sensitive_words: list | None = None
    ) -> SafetyRewriteResult:
        """
        执行改写任务
        :param text: 用户原始输入
        :param sensitive_words: (可选) 上游正则/AC自动机匹配到的敏感词列表
        :return: 字典格式的结果
        """
        # 处理敏感词列表格式
        keywords_str = ", ".join(sensitive_words) if sensitive_words else "无"

        try:
            # 异步调用 (ainvoke) 以利用底层连接池
            result = await self.chain.ainvoke(
                {
                    # 注入 JSON 格式说明
                    "format_instructions": self.parser.get_format_instructions(),
                    "triggered_keywords": keywords_str,
                    "user_input": text,
                }
            )

            return result

        except Exception as e:
            # 生产环境建议结合 logger 记录详细堆栈
            print(f"[IntentService] 改写失败: {e}")
            # 降级策略：如果 LLM 挂了，为了安全起见，通常返回不安全，或者根据策略透传
            return SafetyRewriteResult(
                user_intent="Error",
                rewritten_text="",
                is_safe_now=False,
                hit_rule="SystemError",
            )
