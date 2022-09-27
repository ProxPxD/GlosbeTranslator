from .IntelligentParser.src.intelligentParser import IntelligentParser
from .IntelligentParser.src.parsingException import ParsingException
from .constants import FLAGS
from .layoutAdjusting import layoutAdjusterFactory
from .smartList import SmartList
from .wordFilter import WordFilter
from ..configs.configurations import Configurations, Configs


class TranslatorParser(IntelligentParser):

    _words: SmartList

    def __init__(self, args: list[str]):
        super().__init__(args)
        lang_adjustment_type = Configurations.get_conf(Configs.LANG_SPEC_ADJUSTMENT)
        self._script_adjuster = layoutAdjusterFactory.get_layout_adjuster(lang_adjustment_type)
        self._word_filter = WordFilter()
        self._words = SmartList()
        self._from_lang = SmartList(limit=1)
        self._to_langs = SmartList()

    @property
    def words(self):
        return self._words

    @property
    def from_lang(self):
        return self._from_lang[0] if len(self._from_lang) else None

    @property
    def to_langs(self):
        return self._to_langs

    def parse(self):
        self._args = self._modesManager.filter_modes_out_of_args(self._args)
        error_messages = self._modesManager.validate_modes()
        if error_messages:
            raise ParsingException(error_messages)

        if not (self.modes.is_any_configurational_mode_on() or self.modes.is_any_displayable_mode_on()):
            self._parse_by_mode()
            self._correct_misplaced()
            self._fill_langs_from_config()
            if not self._words:
                raise ParsingException

        self._adjust_to_script()

    def _parse_by_mode(self):
        if self.modes.is_single_mode_on():
            self._parse_normal()
        elif self.modes.is_multi_lang_mode_on():
            self._parse_multi_lang()
        elif self.modes.is_multi_word_mode_on():
            self._parse_multi_word()
        elif self.modes.is_double_multi_mode_on():
            self._parse_double_multi()

    def _parse_normal(self):
        self._words += self._get_arg(0)
        self._from_lang += self._get_arg(1)
        self._to_langs += self._get_range(2)

    def _parse_multi_lang(self):
        self._words += self._get_arg(0)
        self._from_lang += self._get_arg(1)
        self._to_langs += self._get_range(2)
        self._to_langs += self.modes.get_mode_args(FLAGS.MULTI_LANG)

    def _parse_multi_word(self):
        self._from_lang += self._get_arg(0)
        self._to_langs += self._get_arg(1)
        self._words += self._get_range(2)
        self._words += self.modes.get_mode_args(FLAGS.MULTI_WORD)

    def _parse_double_multi(self):
        self._from_lang += self._get_arg(0)
        self._to_langs += self.modes.get_mode_args(FLAGS.MULTI_LANG)
        self._words += self.modes.get_mode_args(FLAGS.MULTI_WORD)

    def _correct_misplaced(self):
        if self._word_filter.is_any_lang_misplaced(*self._from_lang, *self._to_langs):
            self._from_lang, self._to_langs, words = self._word_filter.split_from_from_and_to_langs(self._from_lang, self.to_langs)
            self._words += words
            if self._is_to_lang_in_from_lang():
                self._to_langs += -self._from_lang
            if self._is_from_lang_in_words():
                self._from_lang += -self.words

    def _is_to_lang_in_from_lang(self):
        return self.modes.is_single_mode_on() and self._word_filter.is_any_word_moved_from_to_langs()

    def _is_from_lang_in_words(self):
        return self.modes.is_single_mode_on() or (self.modes.is_multi_lang_mode_on() and self._get_arg(1) is not None)

    def _fill_langs_from_config(self):
        if self.modes.is_multi_lang_mode_on() or self.modes.is_double_multi_mode_on():
            self._fill_langs_from_config_for_m_option()
        else:
            self._fill_langs_from_config_for_not_m_option()

    def _fill_langs_from_config_for_m_option(self):
        if not self._from_lang:
            self._from_lang += Configurations.get_nth_saved_language(0)
        if not self._to_langs:
            self._to_langs += Configurations.load_config_languages(self.from_lang)

    def _fill_langs_from_config_for_not_m_option(self):
        if not self._to_langs:
            self._to_langs += -self._from_lang
        if not self._to_langs:
            self._to_langs += Configurations.get_nth_saved_language(1)
        if not self._from_lang:
            self._from_lang += Configurations.get_nth_saved_language(0)

    def _adjust_to_script(self):
        if self._script_adjuster is not None:
            self._from_lang += self._script_adjuster.adjust_word(-self._from_lang)
            self._to_langs = SmartList(map(self._script_adjuster.adjust_word, self.to_langs))

    def is_translation_mode_on(self):
        return self.from_lang and self._to_langs and self._words