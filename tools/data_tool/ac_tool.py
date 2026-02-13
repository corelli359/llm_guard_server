from typing import Dict
import threading
import ahocorasick
from models import GlobalKeywords, ScenarioKeywords, SensitiveContext
from typing import Any, Union, List, Set
from utils import Promise
from dataclasses import dataclass
from typing import Optional


class SensitiveAutomatonLoaderByDB:
    def __init__(self) -> None:
        self.automaton = None
        self.lock = threading.Lock()

    def load_keywords(
        self,
        word_list: List[Union[GlobalKeywords, ScenarioKeywords]],
        is_global: bool = True,
    ):

        A = ahocorasick.Automaton()
        if is_global:
            for idx, word in enumerate(word_list):
                payload = (word.keyword, word.tag_code)
                A.add_word(word.keyword, payload)
        else:
            for idx, word in enumerate(word_list):
                payload = (
                    word.keyword,
                    word.tag_code,
                    getattr(word, "exemptions", None),
                )
                A.add_word(word.keyword, payload)
        A.make_automaton()
        self.automaton = A

    def scan(
        self, text, exemption_distance: int = 0, ctx: SensitiveContext | None = None
    ) -> dict:
        if not self.automaton:
            raise Exception("NO_WORD_LIST_ERROR")
        contains = {}
        for end_index, payload in self.automaton.iter(text):
            if len(payload) == 3:
                word, tag_code, exemptions = payload
            else:
                word, tag_code = payload
                exemptions = None

            if len(word) <= 1:
                continue

            # 豁免词检查
            if exemptions:
                start_index = end_index - len(word) + 1
                exempted = False
                for ex_word in exemptions:
                    if exemption_distance == 0:
                        # 全文匹配
                        if ex_word in text:
                            exempted = True
                            break
                    else:
                        # 距离匹配
                        window_start = max(0, start_index - exemption_distance)
                        window_end = min(len(text), end_index + 1 + exemption_distance)
                        if ex_word in text[window_start:window_end]:
                            exempted = True
                            break
                if exempted:
                    if ctx:
                        ctx.exemption_set.add(word)
                    continue

            if tag_code not in contains:
                contains[tag_code] = []
            contains[tag_code].append(word)
        return contains


@dataclass
class LoadBase:
    loaded: bool = False


@dataclass
class CustomContainer(LoadBase):
    black_ac: Optional[SensitiveAutomatonLoaderByDB] = None
    white_ac: Optional[Set[str]] = None
    custom_rule: Dict[str, str] | None = None


@dataclass
class CustomVipContainer(LoadBase):
    black_ac: SensitiveAutomatonLoaderByDB | None = None
    black_rule: Dict[str, Any] | None = None
    white_rule: Dict[str, Any] | None = None
    white_ac: SensitiveAutomatonLoaderByDB | None = None
