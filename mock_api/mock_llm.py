import random
from models.request_models import SensitiveContext
from sanic.response import ResponseStream
import asyncio
from enum import StrEnum
from pydantic import BaseModel, Field

safe_threshold = 0.8
MAX_MS: float = 0.13


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


class GuardReponse(BaseModel):
    Safety: GuardSafetyEnum = Field(..., description="安全等级")
    Category: GuardCategoryEnum | None = Field(default=None, description="风险类别")


async def mock_guard(ctx: SensitiveContext):
    is_safe = random.randint(1, 100) <= safe_threshold
    await asyncio.sleep(random.uniform(0.03, MAX_MS))
    guard_response: GuardReponse | None = None
    match is_safe:
        case True:
            guard_response = GuardReponse(Safety=GuardSafetyEnum.SAFE, Category=None)
        case False:
            random_category = random.choice(list(GuardCategoryEnum))
            random_unsafe = random.randint(0, 1)

            guard_response = GuardReponse(
                Safety=(
                    GuardSafetyEnum.UNSAFE
                    if random_unsafe
                    else GuardSafetyEnum.CONTROVERSIAL
                ),
                Category=random_category,
            )
        case _:
            guard_response = GuardReponse(Safety=GuardSafetyEnum.SAFE, Category=None)
    ctx.safety = guard_response.Safety.value
    ctx.category = guard_response.Category
