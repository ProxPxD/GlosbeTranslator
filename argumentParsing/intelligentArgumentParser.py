from abc import ABC
from dataclasses import dataclass

from abstractArgumnetParser import AbstractArgumentParser
from configurations import Configs


@dataclass(frozen=True)
class Modes:
    MULTI_LANG: str = '-m'
    MULTI_LANG_FULL: str = '--multi'
    MULTI_WORD: str = '-w'
    MULTI_WORD_FULL: str = '--word'
    SINGLE: str = '-s'
    SINGLE_FULL: str = '--single'


class IntelligentArgumentParser(AbstractArgumentParser, ABC):

    def __int__(self, args: list[str, ...]):
        super(args)
        self._modes_checkers = [self._is_single_on, self._is_multi_lang_on, self._is_multi_word_on]
        self._modes_on = [False for _ in self._modes_checkers]
        self._mode_parse_methods = [self._parse_normal, self._parse_multi_lang, self._parse_multi_word]

    def parse(self):
        self._collect_modes()
        if self._is_multiple_modes_use():
            raise ValueError(self._modes)  # TODO: expand type

        try:
            i = self._modes_on.index(True)
        except IndexError:
            i = 0

        self._mode_parse_methods[i]()

    def _is_multiple_modes_use(self):
        self._modes_on = [checker() for checker in self._modes_checkers]
        return sum(self._modes_on) > 1

    def _is_multi_lang_on(self):
        return any(mode in (Modes.MULTI_LANG, Modes.MULTI_LANG_FULL) for mode in self._modes)

    def _is_multi_word_on(self):
        return any(mode in (Modes.MULTI_WORD, Modes.MULTI_WORD_FULL) for mode in self._modes)

    def _is_single_on(self):
        return any(mode in (Modes.SINGLE, Modes.SINGLE_FULL) for mode in self._modes)

    def _parse_normal(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_or_config_if_non(1, Configs.FROM_LANG)
        self._to_langs.append(self._get_arg_or_config_if_non(2, Configs.TO_LANG))

    def _parse_multi_lang(self):
        self._words.append(self._args[0])
        self._from_lang = self._args[1]
        self._to_langs = self._args[2:]
        if not self._to_langs:
            pass

    def _parse_multi_word(self):
        self._from_lang = self._args[0]
        self._to_langs.append(self._args[1])
        self._words = self._args[2:]