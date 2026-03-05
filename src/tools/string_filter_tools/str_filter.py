import unicodedata
import re
import base64
from models import SensitiveContext

# 匹配连续的 base64 编码片段（至少 16 个字符，减少误判）
_BASE64_PATTERN = re.compile(
    r"[A-Za-z0-9+/]{16,}={0,2}"
)


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
    ctx.input_prompt = _decode_base64_segments(normalized_text)


def _decode_base64_segments(text: str) -> str:
    """检测并解码文本中的 base64 片段，解码失败或非合法 UTF-8 则保留原文"""
    def _try_decode(match: re.Match) -> str:
        segment = match.group(0)
        # base64 合法长度必须是 4 的倍数
        if len(segment) % 4 != 0:
            return segment
        try:
            decoded = base64.b64decode(segment, validate=True).decode("utf-8")
            # 解码结果应包含可打印字符，否则视为误判
            if decoded.isprintable():
                return decoded
        except Exception:
            pass
        return segment

    return _BASE64_PATTERN.sub(_try_decode, text)
