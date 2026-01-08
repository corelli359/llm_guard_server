import asyncio
from typing import Dict, Optional, Set
from .sensitve_maker import SensitiveAutomatonLoader
# from config import (
    # SENSITIVE_DICT,
    # SENSITIVE_CUSTOMIZE_PATH,
    # SENSITIVE_WHITE_DICT,
    # SENSITIVE_CUSTOMIZE_WHITE_PATH,
    # SENSITIVE_CUSTOMIZE_DICT,
    # CUSTOMIZE_RULE_VIP_BLACK_WORDS_PATH,
    # CUSTOMIZE_RULE_VIP_BLACK_WORDS_DICT,
    # CUSTOMIZE_RULE_VIP_WHITE_WORDS_DICT,
    # CUSTOMIZE_RULE_VIP_WHITE_WORDS_PATH,
# )
from utils import Promise, run_in_async, async_perf_count
from models import SensitiveContext
from sanic.log import logger

from tools.data_tool import DataProvider


_APP_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def _get_lock_by_app_id(app_id: str) -> asyncio.Lock:
    if app_id not in _APP_LOCKS:
        async with _GLOBAL_LOCK:
            if app_id not in _APP_LOCKS:
                _APP_LOCKS[app_id] = asyncio.Lock()
    return _APP_LOCKS[app_id]


# async def customize_ac_load(
#     app_id: str, path: dict, mapping: dict
# ) -> SensitiveAutomatonLoader:

#     def _load(_app_id) -> SensitiveAutomatonLoader:
#         _loader = SensitiveAutomatonLoader(_app_id, path[_app_id])
#         _loader.reload()
#         return _loader

#     ac: Dict[str, str | SensitiveAutomatonLoader] | None = mapping.get(app_id)

#     if not ac:
#         app_id_lock: asyncio.Lock = await _get_lock_by_app_id(app_id)
#         async with app_id_lock:
#             if app_id in mapping:
#                 return mapping[app_id]["data"]
#             loader = await run_in_async(_load, app_id)
#             mapping[app_id] = {"loaded": True, "data": loader}
#             return loader

#     else:
#         return ac["data"]


async def customize_vip_black_load_and_scan_by_db(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()
    ctx.vip_black_words_result = {}
    if ctx.use_vip_black:
        await data_provider.build_ac("vip", ctx.app_id)
        custom_vip = data_provider.custom_vip.get(ctx.app_id)
        if custom_vip and custom_vip.black_ac:
            result = await run_in_async(custom_vip.black_ac.scan, ctx.input_prompt)
            ctx.vip_black_words_result = result


async def customize_vip_white_load_and_scan_by_db(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()
    ctx.vip_white_words_result = {}
    if ctx.use_vip_white:
        await data_provider.build_ac("vip", ctx.app_id)
        custom_vip = data_provider.custom_vip.get(ctx.app_id)
        if custom_vip and custom_vip.white_ac:
            result = await run_in_async(custom_vip.white_ac.scan, ctx.input_prompt)
            ctx.vip_white_words_result = result


# async def customize_vip_load_black_words_and_scan(ctx: SensitiveContext):
#     customize_ac: SensitiveAutomatonLoader | None = None

#     if ctx.use_vip_black and not CUSTOMIZE_RULE_VIP_BLACK_WORDS_DICT.get(ctx.app_id):
#         customize_ac = await customize_ac_load(
#             ctx.app_id,
#             CUSTOMIZE_RULE_VIP_BLACK_WORDS_PATH,
#             CUSTOMIZE_RULE_VIP_BLACK_WORDS_DICT,
#         )
#     else:
#         ctx.vip_black_words_result = {}
#         return

#     if customize_ac:
#         result = await run_in_async(customize_ac.scan, ctx.input_prompt)
#         ctx.vip_black_words_result = result
#     else:
#         ctx.vip_black_words_result = {}


# async def customize_vip_load_white_words_and_scan(ctx: SensitiveContext):
#     customize_ac: SensitiveAutomatonLoader | None = None

#     if ctx.use_vip_black:
#         customize_ac = await customize_ac_load(
#             ctx.app_id,
#             CUSTOMIZE_RULE_VIP_WHITE_WORDS_PATH,
#             CUSTOMIZE_RULE_VIP_WHITE_WORDS_DICT,
#         )
#     else:
#         ctx.vip_white_words_result = {}
#         return

#     if customize_ac:
#         result = await run_in_async(customize_ac.scan, ctx.input_prompt)
#         ctx.vip_white_words_result = result
#     else:
#         ctx.vip_white_words_result = {}


# async def white_load(app_id: str, path: str) -> set:
#     def _read(_path) -> Set:
#         with open(path, "r") as f:
#             lines = f.readlines()
#         data = set([_.strip() for _ in lines])
#         return data

#     if SENSITIVE_WHITE_DICT.get(app_id):
#         return SENSITIVE_WHITE_DICT[app_id]["data"]

#     app_lock: asyncio.Lock = await _get_lock_by_app_id(app_id)

#     async with app_lock:
#         if SENSITIVE_WHITE_DICT.get(app_id):
#             return SENSITIVE_WHITE_DICT[app_id]["data"]
#         try:
#             data = await run_in_async(_read, path)
#             SENSITIVE_WHITE_DICT[app_id] = {"data": data, "loaded": True}
#             return data
#         except Exception as e:
#             logger.error(f"[Error] Load failed: {e}")
#             return set()


# async def customize_load_and_scan(ctx: SensitiveContext):
#     customize_ac: SensitiveAutomatonLoader | None = None

#     if ctx.use_customize_words:
#         customize_ac = await customize_ac_load(
#             ctx.app_id, SENSITIVE_CUSTOMIZE_PATH, SENSITIVE_CUSTOMIZE_DICT
#         )
#     else:
#         ctx.customize_result = {}
#         return

#     if customize_ac:
#         result = await run_in_async(customize_ac.scan, ctx.input_prompt)
#         ctx.customize_result = result
#     else:
#         ctx.customize_result = {}


async def customize_load_and_scan_by_db(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()

    if ctx.use_customize_words:
        if ctx.app_id not in data_provider.custom_ac:
            await data_provider.build_ac("customize", ctx.app_id)
    else:
        ctx.customize_result = {}
        return
    ac_container = data_provider.custom_ac.get(ctx.app_id)
    if ac_container and ac_container.black_ac:
        result = await run_in_async(ac_container.black_ac.scan, ctx.input_prompt)
        ctx.customize_result = result
    else:
        ctx.customize_result = {}


async def global_load_and_scan_by_db(ctx: SensitiveContext):
    data_provider: DataProvider = DataProvider.get_instance()
    if data_provider.global_ac:
        result = await run_in_async(data_provider.global_ac.scan, ctx.input_prompt)
        ctx.global_result = result
    else:
        ctx.global_result = {}


# async def global_load_and_scan(ctx: SensitiveContext):
#     global_ac: SensitiveAutomatonLoader | None = SENSITIVE_DICT.get("global")
#     if global_ac:
#         result = await run_in_async(global_ac.scan, ctx.input_prompt)
#         ctx.global_result = result
#     else:
#         ctx.global_result = {}


async def final_filter(ctx: SensitiveContext):
    ctx.final_result = {}

    merged_keys = ctx.global_result.keys() | ctx.customize_result.keys()
    if not merged_keys:
        return

    data_provider: DataProvider = DataProvider.get_instance()
    this_data = data_provider.custom_ac.get(ctx.app_id)

    white_set: Set[str] = set()

    if ctx.use_customize_white:
        if this_data and this_data.white_ac:
            white_set = this_data.white_ac
    for key in merged_keys:
        global_words = set(ctx.global_result.get(key, []))
        customize_words = set(ctx.customize_result.get(key, []))
        global_words = (
            global_words - customize_words
        )  #  防止一个词在两个通用和自定义中都出现，如果出现则只保留自定义
        merged_words = global_words | customize_words
        final_words = merged_words - white_set

        if final_words:
            ctx.final_result[key] = list(final_words)


async def white_load_and_filter(ctx: SensitiveContext):
    """
    思路：
    if 应用了白名单
        if 尚未加载白名单
            加载
        剩余集合初始化 set
        if 有自定义敏感词设置
            if 自定义敏感词loader不为空
                在自定义set中剔除白名单的内容
                更新到剩余set中
        在通用结果set中剔除白名单内容
        更新到剩余set中
        根据剩余集合的内容作为key，组成最终的数据

    else

        如果有自己定义敏感词结果，则个通用的进行组合
    此处不处理超白和超黑

    """
    ctx.final_result = {}

    merged_keys = ctx.global_result.keys() | ctx.customize_result.keys()
    if not merged_keys:
        return

    data_provider: DataProvider = DataProvider.get_instance()
    this_data = data_provider.custom_ac.get(ctx.app_id)

    white_set: Set[str] = set()

    if ctx.use_customize_white:
        if this_data and this_data.white_ac:
            white_set = this_data.white_ac

    for key in merged_keys:
        global_words = set(ctx.global_result.get(key, []))
        customize_words = set(ctx.customize_result.get(key, []))
        global_words = (
            global_words - customize_words
        )  #  防止一个词在两个通用和自定义中都出现，如果出现则只保留自定义
        merged_words = global_words | customize_words
        final_words = merged_words - white_set

        if final_words:
            ctx.final_result[key] = list(final_words)


class SensitiveTool:
    def __init__(self) -> None:
        self.promise: Promise = Promise()

    def flow(self):
        """
        Docstring for flow
        超黑超白涉及敏感词的在此处加载。
        :param self: Description
        """
        # self.promise.then(
        # customize_vip_black_load_and_scan_by_db,
        # customize_vip_load_black_words_and_scan,
        # customize_vip_white_load_and_scan_by_db,
        # customize_vip_load_white_words_and_scan,
        # )
        self.promise.then(
            customize_load_and_scan_by_db,
            # customize_load_and_scan,
            global_load_and_scan_by_db,
            # global_load_and_scan,
        ).then(
            final_filter
            # white_load_and_filter
        )

    @async_perf_count
    async def execute(self, ctx: SensitiveContext):
        return await self.promise.execute(ctx)
