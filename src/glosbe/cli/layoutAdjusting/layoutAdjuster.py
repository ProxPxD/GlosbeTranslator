from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageSpecificAdjustmentValues:
    NONE: str = 'none'
    NATIVE: str = 'native'
    KEYBOARD: str = 'keyboard'


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


class KeyboardLayoutAdjuster(AbstractLayoutAdjuster):
    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        return {
            'uk': {
                'ут': 'en',
                'зд': 'pl',
                'ву': 'de',
                'ак': 'fr',
                'уі': 'es',
                'яр': 'zh',
                'гл': 'uk',
                'кг': 'ru',
                'ше': 'it',
                '-ц': '-w',
                '-ь': '-m',
                '-і': '-s',
                '-іі': '-ss',
                '-д': '-l',
                '-дд': '-ll',
                '-р': '-h',
            },
            'ru': {

            },
            'de': {
                'яр': 'yh',
            }
        }



class NativeLayoutAdjuster(AbstractLayoutAdjuster):

    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        return {
            'uk': {
                'ен': 'en',
                'пл': 'pl',
                'де': 'de',
                'фр': 'fr',
                'ес': 'es',
                'дж': 'zh',
                'ук': 'uk',
                'ру': 'ru',
                'іт': 'it',
                '-в': '-w',
                '-м': '-m',
                '-с': '-s',
                '-сс': '-ss',
                '-л': '-l',
                '-лл': '-ll',
                '-х': '-h',
            },
            'ru': {
                'ен': 'en',
                'пл': 'pl',
                'де': 'de',
                'фр': 'fr',
                'ес': 'es',
                'дж': 'zh',
                'ук': 'uk',
                'ру': 'ru',
                'ит': 'it',
            },
            'zh': {
                '英': 'en',
                '波': 'pl',
                '德': 'de',
                '法': 'fr',
                '西': 'es',
                '中': 'zh',
                '乌': 'uk',
                '俄': 'ru',
                '意': 'it',
            },
        }
