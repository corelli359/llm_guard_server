"""
文件数据加载器
使用orjson进行高性能JSON解析，从文件系统加载数据
"""
import os
from typing import List, Dict, Any, Tuple
import orjson
from config.data_source_config import get_data_source_config
from models.db_meta import (
    GlobalKeywords,
    MetaTags,
    ScenarioKeywords,
    RuleScenarioPolicy,
    RuleGlobalDefaults,
)
from models import DECISION_MAPPING, DecisionClassifyEnum


class FileDataLoader:
    """文件数据加载器

    从JSON文件加载数据，提供与DAO相同的接口
    """

    def __init__(self):
        self.config = get_data_source_config()
        self.base_path = self.config.file_base_path

    def _read_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """读取JSON文件并解析

        Args:
            filename: 文件名（如 global_keywords.json）

        Returns:
            解析后的数据列表
        """
        file_path = os.path.join(self.base_path, filename)

        if not os.path.exists(file_path):
            # 文件不存在时返回空列表
            return []

        try:
            with open(file_path, "rb") as f:
                # 使用orjson进行高性能解析
                data = orjson.loads(f.read())
                return data if isinstance(data, list) else []
        except Exception as e:
            raise RuntimeError(f"Failed to load {filename}: {str(e)}")

    def _convert_to_model(self, data_list: List[Dict], model_class):
        """将字典列表转换为模型对象列表

        Args:
            data_list: 字典数据列表
            model_class: SQLAlchemy模型类

        Returns:
            模型对象列表
        """
        result = []
        for item in data_list:
            # 创建模型实例
            obj = model_class()
            # 设置属性
            for key, value in item.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            result.append(obj)
        return result

    async def get_all_global_keywords(self) -> List[GlobalKeywords]:
        """获取所有全局关键词"""
        data = self._read_json_file("global_keywords.json")
        return self._convert_to_model(data, GlobalKeywords)

    async def get_all_scenario_keywords(self):
        """获取所有场景关键词，返回元组列表以兼容数据库模式"""
        data = self._read_json_file("scenario_keywords.json")
        models = self._convert_to_model(data, ScenarioKeywords)
        # 返回元组列表，与数据库模式的 Row 格式一致
        return [
            (m.scenario_id, m.keyword, m.tag_code, m.category, m.risk_level)
            for m in models
            if m.is_active
        ]

    async def get_scenario_keywords_by_appid(self, app_id: str) -> List[ScenarioKeywords]:
        """根据app_id获取场景关键词，返回 ORM 对象列表"""
        data = self._read_json_file("scenario_keywords.json")
        models = self._convert_to_model(data, ScenarioKeywords)
        return [kw for kw in models if kw.scenario_id == app_id and kw.is_active]

    async def get_all_scenario_policies(self):
        """获取所有场景策略，返回元组列表以兼容数据库模式"""
        data = self._read_json_file("scenario_policies.json")
        models = self._convert_to_model(data, RuleScenarioPolicy)
        # 返回元组列表，与数据库模式的 Row 格式一致
        # rule 格式: match_value-extra_condition (如果 extra_condition 为空则只有 match_value)
        # 只返回 match_type == "TAG" 且 rule_mode == 1 的记录
        return [
            (
                m.scenario_id,
                f"{m.match_value}-{m.extra_condition or ''}".rstrip('-'),
                m.strategy,
            )
            for m in models
            if m.is_active and m.rule_mode == 1 and m.match_type == "TAG"
        ]

    async def get_scenario_rule_by_appid(self, app_id: str) -> List[RuleScenarioPolicy]:
        """根据app_id获取场景规则，返回 ORM 对象列表"""
        data = self._read_json_file("scenario_policies.json")
        models = self._convert_to_model(data, RuleScenarioPolicy)
        return [
            policy
            for policy in models
            if policy.scenario_id == app_id and policy.is_active and policy.rule_mode == 1
        ]

    async def get_vip_scenario_by_appid(self, app_id: str) -> List[RuleScenarioPolicy]:
        """根据app_id获取VIP场景规则，返回 ORM 对象列表"""
        data = self._read_json_file("scenario_policies.json")
        models = self._convert_to_model(data, RuleScenarioPolicy)
        return [
            policy
            for policy in models
            if policy.scenario_id == app_id and policy.is_active and policy.rule_mode == 0
        ]

    async def get_all_global_defaults(self) -> List[RuleGlobalDefaults]:
        """获取所有全局默认规则"""
        data = self._read_json_file("global_defaults.json")
        return self._convert_to_model(data, RuleGlobalDefaults)

    async def get_all_tags(self) -> List[MetaTags]:
        """获取所有标签"""
        data = self._read_json_file("meta_tags.json")
        return self._convert_to_model(data, MetaTags)

    async def load_all_vip(self):
        """加载所有VIP规则，返回元组列表以兼容数据库模式"""
        data = self._read_json_file("scenario_policies.json")
        models = self._convert_to_model(data, RuleScenarioPolicy)
        # 返回元组列表，与数据库模式的 Row 格式一致
        return [
            (
                m.scenario_id,
                m.match_value,
                m.extra_condition,
                m.strategy,
                m.match_type,
            )
            for m in models
            if m.is_active and m.rule_mode == 0
        ]

    async def load_global_rules(self) -> Dict[str, DecisionClassifyEnum]:
        """加载全局规则（与DBConnectTool接口一致）"""
        results = await self.get_all_global_defaults()
        return {
            f"{item.tag_code}-{item.extra_condition}": DECISION_MAPPING[
                item.strategy.strip()
            ]
            for item in results
        }

    async def load_global_words(self) -> List[GlobalKeywords]:
        """加载全局敏感词（与DBConnectTool接口一致）"""
        return await self.get_all_global_keywords()

    async def load_all_custom_words(self) -> List[ScenarioKeywords]:
        """加载所有自定义敏感词（与DBConnectTool接口一致）"""
        return await self.get_all_scenario_keywords()

    async def load_custom_words(self, app_id: str) -> Tuple[List[ScenarioKeywords], List[ScenarioKeywords]]:
        """加载指定app_id的自定义敏感词，返回黑名单和白名单

        Args:
            app_id: 应用ID

        Returns:
            (black_list, white_list) 元组
        """
        result = await self.get_scenario_keywords_by_appid(app_id)
        black_list = []
        white_list = []
        for row in result:
            if row.category == 1:
                black_list.append(row)
            else:
                white_list.append(row)
        return black_list, white_list

    async def load_all_custom_rules(self) -> List[RuleScenarioPolicy]:
        """加载所有自定义规则（与DBConnectTool接口一致）"""
        return await self.get_all_scenario_policies()

    async def load_custom_rule(self, app_id: str) -> Dict[str, DecisionClassifyEnum]:
        """加载指定app_id的自定义规则

        Args:
            app_id: 应用ID

        Returns:
            规则字典
        """
        results = await self.get_scenario_rule_by_appid(app_id)
        return {
            f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                row.strategy.upper()
            ]
            for row in results
        }

    async def load_vip_scenario_by_app_id(self, app_id: str) -> Tuple[List, Dict, List, Dict]:
        """加载指定app_id的VIP场景规则

        Args:
            app_id: 应用ID

        Returns:
            (vip_black_words, vip_black_rules, vip_white_words, vip_white_rules) 元组
        """
        result = await self.get_vip_scenario_by_appid(app_id)

        vip_black_words = []
        vip_white_words = []
        vip_black_rules: Dict[str, DecisionClassifyEnum] = {}
        vip_white_rules: Dict[str, DecisionClassifyEnum] = {}

        for row in result:
            if row.match_type == "words" and row.strategy == "block":
                vip_black_words.append(row.match_value)
            elif row.match_type == "words" and row.strategy == "pass":
                vip_white_words.append(row.match_value)
            elif row.match_type == "rule" and row.strategy == "block":
                vip_black_rules.update(
                    {
                        f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                            row.strategy.upper()
                        ]
                    }
                )
            elif row.match_type == "rule" and row.strategy == "pass":
                vip_white_rules.update(
                    {
                        f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                            row.strategy.upper()
                        ]
                    }
                )
        return vip_black_words, vip_black_rules, vip_white_words, vip_white_rules

    async def fetch_full_data_package(self) -> dict:
        """并发加载所有数据

        Returns:
            包含所有数据的字典
        """
        import asyncio

        # 并发加载所有数据
        results = await asyncio.gather(
            self.get_all_global_keywords(),
            self.get_all_scenario_keywords(),
            self.get_all_scenario_policies(),
            self.get_all_global_defaults(),
            self.get_all_tags(),
            return_exceptions=True
        )

        return {
            "global_keywords": results[0] if not isinstance(results[0], Exception) else [],
            "scenario_keywords": results[1] if not isinstance(results[1], Exception) else [],
            "scenario_policies": results[2] if not isinstance(results[2], Exception) else [],
            "global_defaults": results[3] if not isinstance(results[3], Exception) else [],
            "tags": results[4] if not isinstance(results[4], Exception) else [],
        }
