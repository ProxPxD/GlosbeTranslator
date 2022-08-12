from typing import Callable, Any

from .configurations import Configurations, Configs
from .constants import FullModes

from .modeManager import ModesManager
from .parsingException import ParsingException


class IntelligentArgumentParser:

    def __init__(self, args: list[str]):
        self._args: list[str] = args[1:]
        self._modesManager = ModesManager()
        self._words = []
        self._from_lang = None
        self._to_langs = []

    @property
    def words(self):
        return self._words

    @property
    def from_lang(self):
        return self._from_lang

    @property
    def to_langs(self):
        return self._to_langs

    @property
    def modes(self) -> ModesManager:
        return self._modesManager

    def is_translation_mode_on(self):
        return self.from_lang is not None

    def parse(self):
        self._args = self._modesManager.filter_modes_out_of_args(self._args)
        error_messages = self._modesManager.validate_modes()
        if error_messages:
            raise ParsingException(error_messages)

        mode: str = self._modesManager.get_translational_mode()
        self._parse_by_mode(mode)

    def _parse_by_mode(self, mode: str):
        if mode == FullModes.SINGLE:
            self._parse_normal()
        elif mode == FullModes.MULTI_WORD:
            self._parse_multi_word()
        elif mode == FullModes.MULTI_LANG:
            self._parse_multi_lang()

    def _parse_normal(self):  # TODO: add excception if no args
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_else_from_config(1)
        self._to_langs.append(self._get_arg_else_from_config(2))

    def _get_arg_else_from_config(self, index: int):
        return self._args[index] if index < len(self._args) else Configurations.get_nth_saved_language(index - 1)

    def _parse_multi_lang(self):  # TODO: add excception if no args
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_or_else(1)
        self._to_langs = self._args[2:]
        if not self._from_lang:
            self._from_lang = Configurations.get_nth_saved_language(0)
        if not self._to_langs:
            self._to_langs = Configurations.load_config_languages(to_skip=self._from_lang)

    def _parse_multi_word(self):
        if self._modesManager.is_mode_explicitly_on(FullModes.MULTI_WORD):
            self._parse_multi_word_explicitly()
        else:
            self._parse_multi_word_implicitly()

    def _parse_multi_word_implicitly(self):
        self._from_lang = self._get_arg_or_else(0)
        self._to_langs.append(self._get_arg_or_else(1))
        self._words = self._args[2:]

    def _parse_multi_word_explicitly(self):
        mode_index: int = self.modes.get_mode_position(FullModes.MULTI_WORD)
        self._from_lang = self._get_arg_before_mode_else_from_config(0, mode_index)
        self._to_langs.append(self._get_arg_before_mode_else_from_config(1, mode_index))
        self._words = self._modesManager.get_mode_args(FullModes.MULTI_WORD)
        if not self._words:
            self._words = self._args[2:]

    def _get_arg_or_else(self, i: int, otherwise: Any = None) -> Any:
        return self._args[i] if i < len(self._args) else otherwise

    def _get_arg_before_mode_else_from_config(self, arg_index: int, mode_index: int):
        return self._args[arg_index] if arg_index < mode_index else Configurations.get_nth_saved_language(arg_index)


