from collections import defaultdict
from typing import Any, Dict, List, Union
from utils import SingleTon, run_in_async
from tools.db_tools import DBConnectTool
from .ac_tool import SensitiveAutomatonLoaderByDB
import asyncio
from .ac_tool import CustomContainer, CustomVipContainer
from models import DecisionClassifyEnum, RuleGlobalDefaults
import pandas as pd
from sanic.log import logger
from utils import Promise
from models import DECISION_MAPPING, ScenarioKeywords
from config.data_source_config import get_data_source_config

_APP_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def get_lock_by_app_id(app_id: str) -> asyncio.Lock:
    if app_id not in _APP_LOCKS:
        async with _GLOBAL_LOCK:
            if app_id not in _APP_LOCKS:
                _APP_LOCKS[app_id] = asyncio.Lock()
    return _APP_LOCKS[app_id]


class DataProvider(metaclass=SingleTon):
    def __init__(self, data_loader: Union[DBConnectTool, Any] = None) -> None:
        """初始化数据提供者

        Args:
            data_loader: 数据加载器，可以是DBConnectTool或FileDataLoader
                        如果为None，会根据配置自动创建
        """
        # 兼容旧代码：如果传入的是DBConnectTool，保存为db_tool
        if isinstance(data_loader, DBConnectTool):
            self.db_tool = data_loader
            self.data_loader = data_loader
        else:
            # 新模式：使用统一的data_loader
            self.data_loader = data_loader
            # 为了兼容性，也设置db_tool属性
            self.db_tool = data_loader if isinstance(data_loader, DBConnectTool) else None

        self._global_ac: SensitiveAutomatonLoaderByDB | None = None

        self._custom_ac: Dict[str, CustomContainer] = {}

        self._vip: Dict[str, CustomVipContainer] = {}

        self._app_super_rules: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._global_rules: Dict[str, DecisionClassifyEnum] = {}

    @property
    def global_rules(self):
        return self._global_rules

    @global_rules.setter
    def global_rules(self, rules):
        self._global_rules = rules

    @property
    def custom_vip(self):
        return self._vip

    @custom_vip.setter
    def custom_vip(self, vip):
        self._vip = vip

    @property
    def custom_ac(self):
        return self._custom_ac

    @custom_ac.setter
    def custom_ac(self, ac):
        self._custom_ac = ac

    @property
    def global_ac(self):
        return self._global_ac

    @global_ac.setter
    def global_ac(self, ac):
        self._global_ac = ac

    async def init_all_data(self):
        promise = Promise()

    async def build_rule(self):
        if not self.global_rules:
            try:
                results: Dict[str, DecisionClassifyEnum] = (
                    await self.data_loader.load_global_rules()
                )
                self.global_rules = results

            except Exception as e:
                logger.error(f"{str(e)}")

    async def build_ac(self, ac_type: str, app_id: str = ""):

        match ac_type:
            case "global":
                data = await self.data_loader.load_global_words()
                self.global_ac = SensitiveAutomatonLoaderByDB()
                await run_in_async(self.global_ac.load_keywords, data)
            case "customize":
                app_id_lock: asyncio.Lock = await get_lock_by_app_id(app_id)
                async with app_id_lock:
                    if app_id and app_id not in self.custom_ac:
                        custom_container = CustomContainer()
                        black_list, white_list = await self.data_loader.load_custom_words(
                            app_id
                        )
                        if black_list:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, black_list)
                            custom_container.black_ac = ac
                        if white_list:
                            custom_container.white_ac = set(
                                [_.keyword for _ in white_list]
                            )

                        custom_rule_list = await self.data_loader.load_custom_rule(app_id)
                        if custom_rule_list:
                            custom_container.custom_rule = custom_rule_list

                        custom_container.loaded = True
                        self.custom_ac[app_id] = custom_container

            case "vip":
                app_id_lock: asyncio.Lock = await get_lock_by_app_id(app_id)
                async with app_id_lock:
                    if app_id and app_id not in self.custom_vip:
                        (
                            vip_black_words,
                            vip_black_rules,
                            vip_white_words,
                            vip_white_rules,
                        ) = await self.data_loader.load_vip_scenario_by_app_id(app_id)
                        vip_container = CustomVipContainer()
                        if vip_black_words:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, vip_black_words)
                            vip_container.black_ac = ac
                        if vip_black_rules:
                            vip_container.black_rule = vip_black_rules
                        if vip_white_rules:
                            vip_container.white_rule = vip_white_rules
                        if vip_white_words:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, vip_black_words)
                            vip_container.white_ac = ac
                        vip_container.loaded = True
                        self.custom_vip[app_id] = vip_container
            case _:
                raise Exception("NO_MATCHED_AC_TYPE_ERROR")


async def load_global_words(ctx: DataProvider):
    data = await ctx.data_loader.load_global_words()
    ctx.global_ac = SensitiveAutomatonLoaderByDB()
    await run_in_async(ctx.global_ac.load_keywords, data)
    logger.info("global sensitive words loaded success!")


async def load_global_rules(ctx: DataProvider):
    results: Dict[str, DecisionClassifyEnum] = await ctx.data_loader.load_global_rules()
    ctx.global_rules = results
    


async def load_custom_words(ctx: DataProvider):
    result_words = await ctx.data_loader.load_all_custom_words()
    result_rules = await ctx.data_loader.load_all_custom_rules()
    df_words = pd.DataFrame(
        result_words,
        columns=["scenario_id", "keyword", "tag_code", "category", "risk_level"],
    )

    df_rules = pd.DataFrame(
        result_rules,
        columns=[
            "scenario_id",
            "rule",
            "strategy",
        ],
    )

    df_rules["strategy"] = df_rules["strategy"].str.upper().map(DECISION_MAPPING)

    # Filter out empty tag_code
    df_words = df_words[df_words["tag_code"].fillna("").str.strip() != ""]

    all_app_ids = set(df_words["scenario_id"].unique()) | set(
        df_rules["scenario_id"].unique()
    )
    words_grouped = df_words.groupby("scenario_id")
    rules_grouped = df_rules.groupby("scenario_id")
    for app_id in all_app_ids:

        if app_id not in ctx.custom_ac:
            custom = CustomContainer()
            ctx.custom_ac[app_id] = custom
        if app_id in words_grouped.groups:
            group = words_grouped.get_group(app_id)
            _df = group[group["category"] == 1]
            # Reconstruct ScenarioKeywords objects
            black_list = [
                ScenarioKeywords(keyword=row.keyword, tag_code=row.tag_code)
                for row in _df.itertuples(index=False)
            ]
            white_list = group[group["category"] == 0]["keyword"].tolist()

            if black_list:
                ac = SensitiveAutomatonLoaderByDB()
                await run_in_async(ac.load_keywords, black_list)
                ctx.custom_ac[app_id].black_ac = ac

            if white_list:
                ctx.custom_ac[app_id].white_ac = set(white_list)
        if app_id in rules_grouped.groups:
            group = rules_grouped.get_group(app_id)
            rules_dict = dict(zip(group["rule_key"], group["strategy"]))
            ctx.custom_ac[app_id].custom_rule = rules_dict
        ctx.custom_ac[app_id].loaded = True
    logger.info("customs sensitive words loaded success!")



async def load_custom_words_else(ctx: DataProvider):
    vip_data = await ctx.data_loader.load_all_vip()

    vip_df = pd.DataFrame(
        vip_data,
        columns=[
            "scenario_id",
            "match_value",
            "extra_condition",
            "strategy",
            "match_type",
        ],
    )

    vip_words_df = vip_df[vip_df["match_type"] == "KEYWORD"]
    vip_words_df["strategy"] = (
        vip_words_df["strategy"].str.upper().map(DECISION_MAPPING)
    )

    vip_tag_df = vip_df[vip_df["match_type"] == "TAG"]
    vip_tag_df["rule_key"] = (
        vip_tag_df["match_value"].astype(str) + "-" + vip_tag_df["extra_condition"]
    )

    all_app_ids = set(vip_df["scenario_id"].unique())

    words_grouped = vip_words_df.groupby("scenario_id")
    rules_grouped = vip_tag_df.groupby("scenario_id")

    for app_id in all_app_ids:
        if app_id not in ctx.custom_vip:
            custom_vip = CustomVipContainer()
            ctx.custom_vip[app_id] = custom_vip
        if app_id in rules_grouped:
            group = rules_grouped.get_group(app_id)
            if not group.empty:
                _df = group[group["strategy"] == DecisionClassifyEnum.REJECT]
                if not _df.empty:
                    rules_dict = dict(zip(_df["rule_key"], _df["strategy"]))
                    ctx.custom_vip[app_id].black_rule = rules_dict
                _df = group[group["strategy"] == DecisionClassifyEnum.PASS]
                if not _df.empty:
                    rules_dict = dict(zip(_df["rule_key"], _df["strategy"]))
                    ctx.custom_vip[app_id].white_rule = rules_dict
        if app_id in words_grouped:
            group = words_grouped.get_group(app_id)
            if not group.empty:
                _df = group[group["strategy"] == DecisionClassifyEnum.PASS]
                if not _df.empty:
                    white_list = list(zip(_df["match_value"], _df["extra_condition"]))
                    if white_list:
                        ac = SensitiveAutomatonLoaderByDB()
                        await run_in_async(ac.load_keywords, white_list)
                        ctx.custom_vip[app_id].white_ac = ac
                _df = group[group["strategy"] != DecisionClassifyEnum.PASS]
                if not _df.empty:
                    black_list = list(zip(_df["match_value"], _df["extra_condition"]))
                    if black_list:
                        ac = SensitiveAutomatonLoaderByDB()
                        await run_in_async(ac.load_keywords, black_list)
                        ctx.custom_vip[app_id].black_ac = ac

        ctx.custom_vip[app_id].loaded = True


class DataInitPromise(Promise):

    def flow(self):
        self.then(load_global_rules, load_global_words).then(
            load_custom_words, load_custom_words_else
        )

    async def run(self, ctx: DataProvider):
        await self.execute(ctx)
