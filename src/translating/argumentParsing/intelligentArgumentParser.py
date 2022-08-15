from typing import Any, Callable

from .configurations import Configurations
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
        return self.from_lang and self._to_langs and self._words

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

        self._remove_nones()

    def _parse_normal(self):  # TODO: add excception if no args
        self._words.append(self._get_arg_or_else(0))
        self._parse_langs_else_get_both_from_configs(1)

    def _parse_multi_lang(self):
        self._words.append(self._get_arg_or_else(0))
        self._from_lang = self._get_arg_else_previous_index_from_config(1)
        self._to_langs = self._args[2:]
        if not self._to_langs:
            self._to_langs = self.modes.get_mode_args(FullModes.MULTI_LANG)
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
        self._parse_langs_else_get_both_from_configs()

        self._words = self._args[2:]
        self._words.extend(self._modesManager.get_mode_args(FullModes.MULTI_WORD))

    def _parse_langs_else_get_both_from_configs(self, offset=0):
        first = self._get_arg_or_else(0 + offset)
        if not first:
            self._from_lang = Configurations.get_nth_saved_language(0)
            self._to_langs.append(Configurations.get_nth_saved_language(1))
        else:
            self._parse_langs_else_get_both_from_configs_depending_on_second(first, offset)

    def _parse_langs_else_get_both_from_configs_depending_on_second(self, first: str, offset=0):
        second = self._get_arg_or_else(1 + offset)
        if second:
            self._from_lang = first
            self._to_langs.append(second)
        else:
            self._from_lang = Configurations.get_nth_saved_language(0)
            self._to_langs.append(first)

    def _get_arg_else_same_from_config(self, index: int):
        return self._get_arg_else_get(index, lambda: Configurations.get_nth_saved_language(index))

    def _get_arg_else_previous_index_from_config(self, index: int):
        return self._get_arg_else_get(index, lambda: Configurations.get_nth_saved_language(index - 1))

    def _get_arg_else_get(self, index: int, func: Callable[[], str]):
        return self._args[index] if index < len(self._args) else func()

    def _get_arg_or_else(self, index: int, otherwise: Any = None) -> Any:
        return self._args[index] if index < len(self._args) else otherwise

    def _remove_nones(self):
        self._to_langs = list(filter(None, self._to_langs))
        self._words = list(filter(None, self._words))

