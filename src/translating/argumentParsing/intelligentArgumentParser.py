from typing import Any, Callable

from . import constants
from .configurations import Configurations, Configs
from .constants import FLAGS
from .layoutAdjusting import layoutAdjusterFactory
from .modeManager import ModesManager
from .parsingException import ParsingException


class IntelligentArgumentParser:

    def __init__(self, args: list[str]):
        self._args: list[str] = args[1:]
        self._modesManager = ModesManager()
        lang_adjustment_type = Configurations.get_conf(Configs.LANG_SPEC_ADJUSTMENT)
        self._scriptAdjuster = layoutAdjusterFactory.get_layout_adjuster(lang_adjustment_type)
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

        self._parse_by_mode()

    def _parse_by_mode(self):
        if self.modes.is_single_mode_on():
            self._parse_normal()
        elif self.modes.is_multi_word_mode_on():
            self._parse_multi_word()
        elif self.modes.is_multi_lang_mode_on():
            self._parse_multi_lang()
        elif self.modes.is_double_multi_mode_on():
            self._parse_double_multi()
        self._remove_nones()

        if self._scriptAdjuster is not None:
            self._adjust_to_script()

    def _parse_normal(self):  # TODO: add excception if no args
        self._words.append(self._get_arg_or_else(0))
        self._parse_langs_else_get_both_from_configs(1)

    def _parse_multi_lang(self):
        self._words.append(self._get_arg_or_else(0))
        from_langs = self._filter_misplaced_langs_to_words(self._get_arg_or_else(1))
        self._from_lang = from_langs[0] if from_langs else Configurations.get_nth_saved_language(0)
        self._to_langs = self._args[2:]

        if not self._to_langs:
            self._to_langs = self.modes.get_mode_args(FLAGS.MULTI_LANG)
        if not self._to_langs:
            self._to_langs = Configurations.load_config_languages(to_skip=self._from_lang)

    def _parse_double_multi(self):
        from_langs = self._filter_misplaced_langs_to_words(self._get_arg_or_else(0))
        self._from_lang = from_langs[0] if from_langs else Configurations.get_nth_saved_language(0)
        self._to_langs = self.modes.get_mode_args(FLAGS.MULTI_LANG)
        self._words = self.modes.get_mode_args(FLAGS.MULTI_WORD)

    def _parse_multi_word(self):
        if self._modesManager.is_mode_explicitly_on(FLAGS.MULTI_WORD):
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
        self._words.extend(self._modesManager.get_mode_args(FLAGS.MULTI_WORD))

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

    def _adjust_to_script(self):
        self._from_lang = self._scriptAdjuster.adjust_word(self._from_lang)
        self._to_langs = list(map(self._scriptAdjuster.adjust_word, self.to_langs))

    def _filter_misplaced_langs_to_words(self, *langs: list):
        criterium = lambda lang: \
                        len(lang) > 3\
                        or any(char not in constants.alphabet for char in lang)
        sorter: tuple[list, list] = ([], self._words)
        for lang in langs:
            sorter[1 if criterium(lang) else 0].append(lang)

        return sorter[0]

    def _remove_nones(self):
        self._to_langs = list(filter(None, self._to_langs))
        self._words = list(filter(None, self._words))

