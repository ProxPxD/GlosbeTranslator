
from .configurations import Configurations, Configs

from .modeManager import ModesManager, ModeTypes, FullModes
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

        if len(self._args):
            mode: str = self._get_current_mode()
            self._modesManager.add_default_mode(mode)
            self._parse_by_mode(mode)

    def _get_current_mode(self) -> str:
        mode = next(self._modesManager.get_modes_turned_on_by_type(ModeTypes.TRANSLATIONAL), None)
        if not mode:
            mode = Configurations.get_conf(Configs.DEFAULT_TRANSLATIONAL_MODE)
        return mode

    def _parse_by_mode(self, mode: str):
        if mode == FullModes.SINGLE:
            self._parse_normal()
        elif mode == FullModes.MULTI_WORD:
            self._parse_multi_word()
        elif mode == FullModes.MULTI_LANG:
            self._parse_multi_lang()

    def _parse_normal(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_else_from_config(1)
        self._to_langs.append(self._get_arg_else_from_config(2))

    def _get_arg_else_from_config(self, index: int):
        return self._args[index] if index < len(self._args) else Configurations.get_nth_saved_language(index - 1)

    def _parse_multi_lang(self):
        self._words.append(self._args[0])
        self._from_lang = self._get_arg_or_else(1)
        self._to_langs = self._args[2:]
        if not self._from_lang:
            self._from_lang = Configurations.get_nth_saved_language(0)
        if not self._to_langs:
            self._to_langs = Configurations.load_config_languages(to_skip=self._from_lang)

    def _parse_multi_word(self):
        self._from_lang = self._args[0]
        self._to_langs.append(self._args[1])
        self._words = self._args[2:]

    def _get_arg_or_else(self, i: int, otherwise: str = None):
        return self._args[i] if i < len(self._args) else otherwise