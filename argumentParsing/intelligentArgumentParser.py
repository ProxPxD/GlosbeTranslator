
from .configurations import Configurations

from .modeManager import ModesManager


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
        if not self._modesManager.validate_modes():
            raise ValueError(self._modesManager)  # TODO: expand type

        if len(self._args):
            self._parse_by_mode()

    def _parse_by_mode(self):
        if self._modesManager.is_single_mode_on():
            self._parse_normal()
        elif self._modesManager.is_multi_lang_mode_on():
            self._parse_multi_lang()
        elif self._modesManager.is_multi_word_mode_on():
            self._parse_multi_word()

    def _parse_normal(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_else_from_config(1)
        self._to_langs.append(self._get_arg_else_from_config(2))

    def _get_arg_else_from_config(self, index: int):
        return self._args[index] if index < len(self._args) else Configurations.get_nth_saved_language(index - 1)

    def _parse_multi_lang(self):
        self._words.append(self._args[0])
        self._from_lang = self._args[1]
        self._to_langs = self._args[2:]
        if not self._to_langs:
            self._to_langs = Configurations.load_config_languages(to_skip=self._from_lang)

    def _parse_multi_word(self):
        self._from_lang = self._args[0]
        self._to_langs.append(self._args[1])
        self._words = self._args[2:]