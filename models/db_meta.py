# from sqlalchemy import Column, String, Integer, Boolean, DateTime, CHAR
# from sqlalchemy.ext.declarative import declarative_base
# from pydantic import BaseModel
# from typing import Optional

# Base = declarative_base()

# # --- 数据库表映射 (SQLAlchemy Models) ---


# class GlobalKeywords(Base):
#     __tablename__ = "lib_global_keywords"
#     id = Column(CHAR(36), primary_key=True)
#     keyword = Column(String)
#     tag_code = Column(String)
#     risk_level = Column(String)
#     is_active = Column(Boolean)


# class MetaTags(Base):
#     """元数据标签表"""

#     __tablename__ = "meta_tags"

#     id = Column(CHAR(36), primary_key=True)
#     tag_code = Column(String(64), unique=True, nullable=False)
#     tag_name = Column(String(128), nullable=False)
#     parent_code = Column(String(64), nullable=True)
#     level = Column(Integer, default=2)
#     is_active = Column(Boolean, default=True, nullable=False)


# class ScenarioKeywords(Base):
#     __tablename__ = "lib_scenario_keywords"
#     CATEGORY_WHITE = 0  # 放行
#     CATEGORY_BLACK = 1  # 拦截
#     id = Column(CHAR(36), primary_key=True)
#     scenario_id = Column(String)
#     keyword = Column(String)
#     tag_code = Column(String)
#     risk_level = Column(String)
#     is_active = Column(Boolean)
#     category = Column(Integer, default=CATEGORY_BLACK, nullable=False, comment='0:白, 1:黑')


# class RuleScenarioPolicy(Base):
#     __tablename__ = "rule_scenario_policy"
#     id = Column(CHAR(36), primary_key=True)
#     scenario_id = Column(String)
#     match_type = Column(String)  # KEYWORD / TAG
#     match_value = Column(String)
#     extra_condition = Column(String, nullable=True)
#     strategy = Column(String)  # BLOCK / PASS / REWRITE
#     is_active = Column(Boolean)


# class RuleGlobalDefaults(Base):
#     __tablename__ = "rule_global_defaults"
#     id = Column(CHAR(36), primary_key=True)
#     tag_code = Column(String)
#     extra_condition = Column(String, nullable=True)
#     strategy = Column(String)
#     is_active = Column(Boolean)
from typing import Optional
from sqlalchemy import String, Integer, Boolean, CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 1. 定义新的 Base 类 (继承 DeclarativeBase)
class Base(DeclarativeBase):
    pass


# --- 数据库表映射 (SQLAlchemy 2.0 Models) ---


class GlobalKeywords(Base):
    __tablename__ = "lib_global_keywords"

    # Mapped[str] 告诉 IDE 这是个字符串
    # mapped_column(...) 定义数据库细节
    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255))
    tag_code: Mapped[str] = mapped_column(String(64))
    risk_level: Mapped[str] = mapped_column(String(32))
    # Mapped[bool] 告诉 IDE 这是布尔值
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class MetaTags(Base):
    """元数据标签表"""

    __tablename__ = "meta_tags"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[str] = mapped_column(String(64), unique=True)
    tag_name: Mapped[str] = mapped_column(String(128))

    # Optional[str] 表示该字段在 Python 中可以是 None
    # nullable=True 表示数据库中允许 NULL
    parent_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    level: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ScenarioKeywords(Base):
    __tablename__ = "lib_scenario_keywords"

    CATEGORY_WHITE = 0
    CATEGORY_BLACK = 1

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)
    keyword: Mapped[str] = mapped_column(String(255))
    tag_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[int] = mapped_column(
        Integer, default=CATEGORY_BLACK, comment="0:白, 1:黑"
    )


class RuleScenarioPolicy(Base):
    __tablename__ = "rule_scenario_policy"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(String(64))
    match_type: Mapped[str] = mapped_column(String(16))  # KEYWORD / TAG
    match_value: Mapped[str] = mapped_column(String(255))
    rule_mode: Mapped[int] = mapped_column(Integer, default=2)
    extra_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    strategy: Mapped[str] = mapped_column(String(32))  # BLOCK / PASS / REWRITE
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class RuleGlobalDefaults(Base):
    __tablename__ = "rule_global_defaults"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[str] = mapped_column(String(64))

    extra_condition: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    strategy: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
