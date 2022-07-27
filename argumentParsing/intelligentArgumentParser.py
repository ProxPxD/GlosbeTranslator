from dataclasses import dataclass

from . import configurations
from .abstractArgumnetParser import AbstractArgumentParser
from .configurations import Configs

# TODO: refactor class potentially


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
        self._modes: Mode = None

    def _parse_normal(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_else_none(1)
        self._to_langs.append(self._get_arg_else_none(2))

        if not self.from_lang or not self.to_langs:
            self._load_args_from_memory(1)

    @property
    def modes(self):
        return self._modes

    def parse(self):
        self._separate_modes__from_args()
        if self._modes.is_multiple_modes_use():
            raise ValueError(self._modes)  # TODO: expand type

        self._parse_by_mode()

    def _parse_by_mode(self):
        if self._modes.is_multi_lang_mode():
            self._parse_multi_lang()
        elif self._modes.is_multi_word_mode():
            self._parse_multi_word()
        elif self._modes.is_single_mode():
            self._parse_normal()

    def _separate_modes__from_args(self):
        modes = [arg for arg in self._args if self._is_mode(arg)]
        self._modes = Mode(modes)
        self._args = [arg for arg in self._args if not self._is_mode(arg)]

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
            self._to_langs = self._load_config_languages()

    def _load_config_languages(self):
        to_langs: list = configurations.get_conf(Configs.SAVED_LANGS)
        to_langs.remove(self._from_lang)
        limit: int = configurations.get_conf(Configs.LANG_LIMIT)
        if len(to_langs) > limit:
            to_langs = self._to_langs[0:limit]
        return to_langs

    def _parse_multi_word(self):
        self._from_lang = self._args[0]
        self._to_langs.append(self._args[1])
        self._words = self._args[2:]


class Mode:

    def __init__(self, modes: list[str, ...]):
        self._modes_on = {Modes.SINGLE: self._is_single_on(modes),
                          Modes.MULTI_LANG: self._is_multi_lang_on(modes),
                          Modes.MULTI_WORD: self._is_multi_word_on(modes)}

    def is_multi_lang_mode(self):
        return self.is_mode(Modes.MULTI_LANG)

    def is_multi_word_mode(self):
        return self.is_mode(Modes.MULTI_WORD)

    def is_single_mode(self):
        return not any(self._modes_on.values()) or self.is_mode(Modes.SINGLE)

    def is_mode(self, mode: str):
        return self._modes_on[mode]

    def is_multiple_modes_use(self):
        return sum(self._modes_on.values()) > 1

    def _is_multi_lang_on(self, modes: [str, ...]):
        return any(mode in (Modes.MULTI_LANG, Modes.MULTI_LANG_FULL) for mode in modes)

    def _is_multi_word_on(self, modes: [str, ...]):
        return any(mode in (Modes.MULTI_WORD, Modes.MULTI_WORD_FULL) for mode in modes)

    def _is_single_on(self, modes: [str, ...]):
        return any(mode in (Modes.SINGLE, Modes.SINGLE_FULL) for mode in modes)