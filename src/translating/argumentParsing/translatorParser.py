from .constants import FLAGS
from ..configs.configurations import Configurations


class TranslatorCli(Cli):

    def __init__(self, args: list[str]):
        root = Root('root')
        root.set_only_hidden_nodes()
        # Collections
        current_modes = root.add_collection('current_modes')
        current_modes.set_type(str)
        self.default_mode = 'before get mode'
        current_modes.set_get_default(self.get_default_mode)
        from_langs = root.add_collection('from_langs', 1)
        to_langs = root.add_collection('to_langs')
        words = root.add_collection('words')

        # Flags
        single_flag = root.add_global_flag('--single', '-s')
        word_flag = root.add_global_flag('--word', '-w')
        lang_flag = root.add_global_flag('--multi', '-m')
        single_flag.when_active_add_name_to(current_modes)  # same as 1
        current_modes.add_to_add_names(lang_flag, word_flag)  # same as 1
        word_flag.set_limit(None, storage=words)  # infinite
        lang_flag.set_limit(None, storage=to_langs)  # infinite

        test_string = 'test'
        words.append(test_string)
        self.assertEqual(test_string, word_flag.get(), msg='Flag has a storage that is not the same place as the original one')
        words.clear()

        # Hidden nodes
        join_to_str = lambda: f'{from_langs.get()}/{to_langs.get()}/{words.get()}'
        single_node = root.add_hidden_node('single', action=join_to_str)
        word_node = root.add_hidden_node('word', action=join_to_str)
        lang_node = root.add_hidden_node('lang', action=join_to_str)
        double_multi_node = root.add_hidden_node('double', action=join_to_str)

        # Hidden nodes activation rules
        single_node.set_active_on_flags_in_collection(current_modes, single_flag, but_not=[word_flag, lang_flag])
        word_node.set_active_on_flags_in_collection(current_modes, word_flag)
        word_node.set_inactive_on_flags_in_collection(current_modes, lang_flag, single_flag)
        lang_node.set_active_on_flags_in_collection(current_modes, lang_flag, but_not=word_flag)
        double_multi_node.set_active_on_flags_in_collection(current_modes, lang_flag, word_flag, but_not=single_flag)

        # Params
        from_langs.set_get_default(lambda: self.get_nth_lang(0))
        to_langs.add_get_default_if_or(lambda: self.get_nth_lang(1), single_node.is_active, word_node.is_active)
        to_langs.add_get_default_if_or(lambda: self.get_first_n_langs(self.limit), lang_node.is_active, double_multi_node.is_active)
        # Single's params
        single_node.set_params_order('word from_lang to_lang')
        single_node.set_params_order('word to_lang')
        single_node.set_params_order('word')
        single_node.set_params('word', 'from_lang', 'to_lang', storages=(words, from_langs, to_langs))
        # Lang's params
        lang_node.set_params('word', 'from_lang', 'to_langs', storages=(words, from_langs, to_langs))
        lang_node.set_params_order('words from_lang to_langs')
        lang_node.set_default_setting_order('from_lang')
        # Word's params
        word_node.set_params('word', 'from_lang', 'to_langs', storages=(words, from_langs, to_langs))
        word_node.set_params_order('from_lang to_langs words')
        lang_node.set_default_setting_order('from_lang', 'to_langs')
        # Double's params
        double_multi_node.set_params('word', 'from_lang', 'to_langs', storages=(words, from_langs, to_langs))
        double_multi_node.set_params_order('from_lang')
        double_multi_node.set_params_order('')
        super().__init__(root, args)

    # TODO: refactor and remove the below

    @property
    def words(self):
        return self._words

    @property
    def from_lang(self):
        return self._from_lang[0] if len(self._from_lang) else None

    @property
    def to_langs(self):
        return self._to_langs

    # def parse(self):
    #     super().parse()  # TODO: temp
    #
    #     if not (self.modes.is_any_configurational_mode_on() or self.modes.is_any_displayable_mode_on()):
    #         self._parse_by_mode()
    #         self._correct_misplaced()
    #         self._fill_langs_from_config()
    #         if not self._words:
    #             raise ParsingException
    #
    #     self._adjust_to_script()

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

    # def _adjust_to_script(self):
    #     if self._script_adjuster is not None:
    #         self._from_lang += self._script_adjuster.adjust_word(-self._from_lang)
    #         self._to_langs = SmartList(map(self._script_adjuster.adjust_word, self.to_langs))

    def is_translation_mode_on(self):
        return self.from_lang and self._to_langs and self._words