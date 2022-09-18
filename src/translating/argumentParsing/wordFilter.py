from . import constants
from .smartList import SmartList

tupleLists_2 = tuple[SmartList[str], SmartList[str]]
tupleLists_3 = tuple[SmartList[str], SmartList[str], SmartList[str]]


class WordFilter:

    def __init__(self):
        self._is_any_word_moved_from_from_langs = False
        self._is_any_word_moved_from_to_langs = False

    def reset(self):
        self._is_any_word_moved_from_from_langs = False
        self._is_any_word_moved_from_to_langs = False

    def is_any_word_moved_from_from_langs(self) -> bool:
        return self._is_any_word_moved_from_from_langs

    def is_any_word_moved_from_to_langs(self) -> bool:
        return self._is_any_word_moved_from_to_langs

    def is_word(self, to_test: str) -> bool:
        return len(to_test) > 3 or any(char not in constants.alphabet for char in to_test)

    def is_any_lang_misplaced(self, *to_check: str):
        return any(self.is_word(elem) for elem in to_check)

    def _membership(self, to_test):
        return 1 if self.is_word(to_test) else 0

    def split_into_langs_and_words(self, to_split: SmartList[str]) -> tupleLists_2:
        langs_words: tupleLists_2 = (SmartList(), SmartList())
        for to_test in to_split:
            langs_words[self._membership(to_test)].append(to_test)
        return langs_words

    def split_from_from_and_to_langs(self, from_lang: SmartList[str], to_langs: SmartList[str]) -> tupleLists_3:
        new_from_lang, from_langs_words = self.split_into_langs_and_words(from_lang)
        new_to_lang, to_langs_words = self.split_into_langs_and_words(to_langs)
        if from_langs_words:
            self._is_any_word_moved_from_from_langs = True
        if to_langs_words:
            self._is_any_word_moved_from_to_langs = True
        return new_from_lang, new_to_lang, from_langs_words + to_langs_words
