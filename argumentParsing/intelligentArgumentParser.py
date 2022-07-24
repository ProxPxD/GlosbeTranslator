from dataclasses import dataclass

from . import configurations
from .abstractArgumnetParser import AbstractArgumentParser
from .configurations import Configs


@dataclass(frozen=True)
class Modes:
    MULTI_LANG: str = '-m'
    MULTI_LANG_FULL: str = '--multi'
    MULTI_WORD: str = '-w'
    MULTI_WORD_FULL: str = '--word'
    SINGLE: str = '-s'
    SINGLE_FULL: str = '--single'


class IntelligentArgumentParser(AbstractArgumentParser):

    def __init__(self, args: list[str, ...]):
        super().__init__(args)
        self._mode_names = [Modes.SINGLE, Modes.MULTI_LANG, Modes.MULTI_WORD]
        self._modes_on = {name: False for name in self._mode_names}
        self._modes_checkers = {Modes.SINGLE: self._is_single_on,
                                Modes.MULTI_LANG: self._is_multi_lang_on,
                                Modes.MULTI_WORD: self._is_multi_word_on}
        self._mode_parse_methods = {Modes.SINGLE: self._parse_normal,
                                    Modes.MULTI_LANG: self._parse_multi_lang,
                                    Modes.MULTI_WORD: self._parse_multi_word}

    @property
    def modes(self):
        return self._modes_on

    def is_multi_lang_mode(self):
        return self.is_mode(Modes.MULTI_LANG)

    def is_multi_word_mode(self):
        return self.is_mode(Modes.MULTI_WORD)

    def is_single_mode(self):
        return not any(self._modes_on.values()) or self.is_mode(Modes.SINGLE)

    def is_mode(self, mode: str):
        return self._modes_on[mode]

    def parse(self):
        self._collect_modes()
        if self._is_multiple_modes_use():
            raise ValueError(self._modes)  # TODO: expand type

        mode = next((mode for mode, val in self._modes_on.items() if val), Modes.SINGLE)
        self._mode_parse_methods[mode]()

    def _is_multiple_modes_use(self):
        self._modes_on = {mode: checker() for mode, checker in self._modes_checkers.items()}
        return sum(self._modes_on.values()) > 1

    def _is_multi_lang_on(self):
        return any(mode in (Modes.MULTI_LANG, Modes.MULTI_LANG_FULL) for mode in self._modes)

    def _is_multi_word_on(self):
        return any(mode in (Modes.MULTI_WORD, Modes.MULTI_WORD_FULL) for mode in self._modes)

    def _is_single_on(self):
        return any(mode in (Modes.SINGLE, Modes.SINGLE_FULL) for mode in self._modes)

    def _parse_normal(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_else_none(1)
        self._to_langs.append(self._get_arg_else_none(2))

        if not self.from_lang or not self.to_langs:
            self._load_args_from_memory(1)

    def _load_args_from_memory(self, to_lang_limit: int):
        langs = configurations.get_conf(Configs.SAVED_LANGS)
        if not self.from_lang:
            self._from_lang = langs[0]
        if not self._to_langs:
            self._to_langs.extend(langs[1:to_lang_limit+1])

    def _parse_multi_lang(self):
        self._words.append(self._args[0])
        self._from_lang = self._args[1]
        self._to_langs = self._args[2:]
        if not self._to_langs:
            self._to_langs = configurations.get_conf(Configs.SAVED_LANGS)

    def _parse_multi_word(self):
        self._from_lang = self._args[0]
        self._to_langs.append(self._args[1])
        self._words = self._args[2:]