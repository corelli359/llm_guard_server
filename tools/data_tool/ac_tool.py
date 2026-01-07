import threading
import ahocorasick
from models import GlobalKeywords, ScenarioKeywords
from typing import Any, Union, List, Set
from utils import Promise
from dataclasses import dataclass
from typing import Optional


class SensitiveAutomatonLoaderByDB:
    def __init__(self) -> None:
        self.automaton = None
        self.lock = threading.Lock()

    def load_keywords(self, word_list: List[Union[GlobalKeywords, ScenarioKeywords]]):

        A = ahocorasick.Automaton()
        for idx, word in enumerate(word_list):
            payload = (word.keyword, word.tag_code)
            A.add_word(word.keyword, payload)
        A.make_automaton()
        self.automaton = A

    def scan(self, text) -> dict:
        if not self.automaton:
            raise Exception("NO_WORD_LIST_ERROR")
        contains = {}
        for _, (word, tag_code) in self.automaton.iter(text):
            if tag_code not in contains:
                contains[tag_code] = []
            if len(word) > 1:
                contains[tag_code].append(word)
        return contains


@dataclass
class LoadBase:
    loaded: bool = False


@dataclass
class CustomAcContainer(LoadBase):
    black_ac: Optional[SensitiveAutomatonLoaderByDB] = None
    white_ac: Optional[Set[str]] = None


@dataclass
class CustomVipContainer(LoadBase):
    black_ac: SensitiveAutomatonLoaderByDB | None = None
    black_rule: Set[str] | None = None
    white_rule: Set[str] | None = None
    white_ac: SensitiveAutomatonLoaderByDB | None = None
