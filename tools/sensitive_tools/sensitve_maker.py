import threading
# from config import SENSITIVE_DICT
import ahocorasick
from models import GlobalKeywords, ScenarioKeywords
import random
from typing import Union, List


class SensitiveAutomatonLoaderByDB:
    def __init__(self) -> None:
        self.automaton = None
        self.lock = threading.Lock()

    def load_keywords(self, word_list: List[Union[GlobalKeywords, ScenarioKeywords]]):

        A = ahocorasick.Automaton()
        for idx, word in enumerate(word_list):
            A.add_word(word.keyword, word.tag_code)
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


class SensitiveAutomatonLoader:
    def __init__(self, name: str, path: str):
        self.automaton = None
        self.name = name
        self.path = path
        self.lock = threading.Lock()

    def load_from_db(self, word_list):
        pass

    def loader(self, word_list):
        A = ahocorasick.Automaton()
        for idx, word in enumerate(word_list):
            payload = (word, f'{random.choices(["A", "B"])[0]}-1')
            A.add_word(word, payload)
        A.make_automaton()
        self.automaton = A


    def scan(self, text) -> dict:
        if not self.automaton:
            raise Exception("NO_WORD_LIST_ERROR")
        # 只要找到一个匹配就返回 True
        contains = {}
        for _, (word, level) in self.automaton.iter(text):
            if level not in contains:
                contains[level] = []
            if len(word) > 1:
                contains[level].append(word)
        return contains
