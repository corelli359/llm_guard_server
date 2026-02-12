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
        
        # Aggregate tags for the same keyword
        temp_dict = {}
        for word in word_list:
            if word.keyword not in temp_dict:
                temp_dict[word.keyword] = set()
            temp_dict[word.keyword].add(word.tag_code)
            
        for keyword, tags in temp_dict.items():
            A.add_word(keyword, list(tags))
            
        A.make_automaton()
        self.automaton = A

    def scan(self, text) -> dict:
        if not self.automaton:
            raise Exception("NO_WORD_LIST_ERROR")
        contains = {}
        # Payload is now a list of tags
        for _, (tag_list) in self.automaton.iter(text):
            # ahocorasick iter returns (end_index, value)
            # wait, the original code was: for _, (word, tag_code) in self.automaton.iter(text):
            # Use strict type checking or testing to confirm return format.
            # Usually .iter() returns (end_index, value).
            # The value is what we stored: list(tags)
            # But the original code unpacked it as (word, tag_code) ??? 
            # Ah, check ahocorasick documentation or usage.
            # If stored value is just tag_code, then value is tag_code.
            # But where did 'word' come from in the original tuple unpacking?
            # Maybe the user was wrong in original code or I am misremembering ahocorasick.
            # pyahocorasick iter returns (end_index, value).
            # If original stored (word.keyword, word.tag_code) as payload? 
            # Original code: A.add_word(word.keyword, word.tag_code) -> Payload is tag_code.
            # Original scan: for _, (word, tag_code) in self.automaton.iter(text):
            # This implies payload was a tuple? 
            # Let's check the original code again.
            pass
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
