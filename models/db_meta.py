from sqlalchemy import Column, String, Integer, Boolean, DateTime, CHAR
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

# --- 数据库表映射 (SQLAlchemy Models) ---


class GlobalKeywords(Base):
    __tablename__ = "lib_global_keywords"
    id = Column(CHAR(36), primary_key=True)
    keyword = Column(String)
    tag_code = Column(String)
    risk_level = Column(String)
    is_active = Column(Boolean)


class MetaTags(Base):
    """元数据标签表"""

    __tablename__ = "meta_tags"

    id = Column(CHAR(36), primary_key=True)
    tag_code = Column(String(64), unique=True, nullable=False)
    tag_name = Column(String(128), nullable=False)
    parent_code = Column(String(64), nullable=True)
    level = Column(Integer, default=2)
    is_active = Column(Boolean, default=True, nullable=False)


class ScenarioKeywords(Base):
    __tablename__ = "lib_scenario_keywords"
    id = Column(CHAR(36), primary_key=True)
    scenario_id = Column(String)
    keyword = Column(String)
    tag_code = Column(String)
    risk_level = Column(String)
    is_active = Column(Boolean)


class RuleScenarioPolicy(Base):
    __tablename__ = "rule_scenario_policy"
    id = Column(CHAR(36), primary_key=True)
    scenario_id = Column(String)
    match_type = Column(String)  # KEYWORD / TAG
    match_value = Column(String)
    extra_condition = Column(String, nullable=True)
    strategy = Column(String)  # BLOCK / PASS / REWRITE
    is_active = Column(Boolean)


class RuleGlobalDefaults(Base):
    __tablename__ = "rule_global_defaults"
    id = Column(CHAR(36), primary_key=True)
    tag_code = Column(String)
    extra_condition = Column(String, nullable=True)
    strategy = Column(String)
    is_active = Column(Boolean)
