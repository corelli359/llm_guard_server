import threading

from config import SENSITIVE_DICT
import ahocorasick

import random


class SensitiveAutomatonLoader:
    def __init__(self, name: str, path: str):
        self.automaton = None
        self.name = name
        self.path = path
        self.lock = threading.Lock()

    def loader(self, word_list):
        A = ahocorasick.Automaton()
        for idx, word in enumerate(word_list):
            payload = (word, f'{random.choices(["A", "B"])[0]}-1')
            A.add_word(word, payload)
        A.make_automaton()
        self.automaton = A

    def reload(self, flush: bool = False):
        if flush or self.name not in SENSITIVE_DICT:
            with open(self.path, "r") as f:
                word_list = f.readlines()
            word_list = [_.strip() for _ in word_list]
            self.loader(word_list)

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
