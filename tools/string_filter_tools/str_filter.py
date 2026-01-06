import unicodedata
import re
from models import SensitiveContext


def unicode_input(text: str) -> str:
    # 1. Unicode 归一化 (NFKC 模式)
    # 这一步会将全角字符转半角，将兼容字符转标准字符
    # 例如：'Ｈｅｌｌｏ' -> 'Hello', '①' -> '1'
    normalized_text = unicodedata.normalize("NFKC", text)

    # 2. 移除零宽字符 (使用上面定义的正则)
    pattern = r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u202a-\u202e]"
    clean_text = re.sub(pattern, "", normalized_text)

    return clean_text.strip()


def remove_control_chars(ctx: SensitiveContext):
    """
    # 1. Unicode 归一化 (NFKC 模式)
    # 这一步会将全角字符转半角，将兼容字符转标准字符
    # 例如：'Ｈｅｌｌｏ' -> 'Hello', '①' -> '1'
    # 2.移除所有 Unicode 类别为 'Cf' (Format) 的字符。
    # 包括零宽空格、双向控制符等。
    """
    normalized_text = unicodedata.normalize("NFKC", ctx.input_prompt)

    normalized_text = "".join(
        ch for ch in normalized_text if unicodedata.category(ch) != "Cf"
    )

    ctx.original_input_prompt = ctx.input_prompt
    ctx.input_prompt = normalized_text
