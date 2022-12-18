from __future__ import annotations

import abc


class AbstractLayoutAdjuster(abc.ABC):

    def __init__(self, adjustment_lang: str = None):
        self._adjustment_lang = None
        self._dictionary = {}
        self.set_adjustment_lang(adjustment_lang)

    def set_adjustment_lang(self, adjustment_lang):
        if adjustment_lang:
            self._adjustment_lang = adjustment_lang
            self._dictionary = self._get_dictionary()[adjustment_lang] if adjustment_lang in self._get_dictionary() else {}

    def adjust_word(self, word: str) -> str:
        return self._dictionary[word] if word in self._dictionary else word

    @abc.abstractmethod
    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        pass
