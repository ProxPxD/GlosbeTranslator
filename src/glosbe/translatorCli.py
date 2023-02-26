from itertools import chain, islice
from typing import Callable, Iterable

from more_itertools import unique_everseen
from pandas import DataFrame
from smartcli import Parameter, HiddenNode, Cli, Root, CliCollection, Flag

from .configurations import Configurations
from .constants import FLAGS as F
from .layoutAdjusting.layoutAdjuster import LayoutAdjustmentsMethods, LayoutAdjusterFactory
from .translating.scrapping import TranslationTypes, TranslationResult, Scrapper
from .translatingPrinting.configDisplayer import ConfigDisplayer
from .translatingPrinting.formatting import TableFormatter
from .translatingPrinting.translationPrinter import TranslationPrinter
from .wordFilter import WordFilter

CURRENT_MODES_COL = 'current_modes'
FROM_LANGS_COL = 'from_langs'
TO_LANGS_COL = 'to_langs'
WORDS_COL = 'words'
CONFS_COL = 'configurations'

just_set = (F.C.LANG_LIMIT_LONG_FLAG, F.C.DOUBLE_MODE_STYLE_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_METHOD_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_LANG_LONG_FLAG)
just_display = (F.C.LANG_LIMIT_LONG_FLAG, F.C.DEFAULT_MODE_LONG_FLAG, F.C.LANGS_SHOW_LONG_FLAG, F.C.DOUBLE_MODE_STYLE_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_METHOD_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_LANG_LONG_FLAG)
display_with_arg = (F.C.LAST_LANG_LONG_FLAG, )
other_config = (F.C.LAST_1_LONG_FLAG, F.C.LAST_2_LONG_FLAG, F.C.ADD_LANG_LONG_FLAG, F.C.REMOVE_LANG_LONG_FLAG, F.C.SETTINGS_LONG_FLAG, F.F.SYNOPSIS_LONG_FLAG)

modes = (F.M.SINGLE_LONG_FLAG, F.M.LANG_LONG_FLAG, F.M.WORD_LONG_FLAG)


class TranslatorCli(Cli):

    def __init__(self, args: list[str] = None):
        super().__init__(args=args)
        self._current_modes: CliCollection
        self._from_langs: CliCollection
        self._to_langs: CliCollection
        self._words: CliCollection
        self._non_translation_flags: CliCollection

        self._to_langs_param: Parameter
        self._words_param: Parameter
        self._configuration_args: Parameter

        self._configuration_node: HiddenNode
        self._display_node: HiddenNode
        self._translation_node: HiddenNode

        self._single_node: HiddenNode
        self._word_node: HiddenNode
        self._lang_node: HiddenNode
        self._double_multi_node: HiddenNode
        self._conjugation_node: HiddenNode

        self._from_langs: Flag
        self._to_langs: Flag
        self._words: Flag
        self._conjugation_flag: Flag
        self._cconjugation_flag: Flag

        self._scrapper = Scrapper()
        self._translation_printer = TranslationPrinter()
        self._word_filter = WordFilter()
        self._is_translating = True

        self._root = Root('root')
        self._create_collections()
        self._create_flags()
        self._create_params()
        self._create_hidden_nodes()

        self._configure_collections()
        self._configure_flags()
        self._configure_hidden_nodes()
        self._configure_cli()

        self._add_translation_args_preprocessing_actions()

        self._create_help()

    def turn_on_translating(self) -> None:
        self._is_translating = True

    def turn_off_translating(self) -> None:
        self._is_translating = False

    @property
    def words(self):
        return self._words.get_as_list()

    @property
    def from_lang(self) -> list[str]:
        return self._from_langs.get()

    @property
    def to_langs(self) -> list[str]:
        return self._to_langs.get_as_list()

    @property
    def langs(self) -> list[str]:
        return [self.from_lang] + self.to_langs

    def _create_collections(self) -> None:
        self._current_modes = self._root.add_collection(CURRENT_MODES_COL)
        self._from_langs = self._root.add_collection(FROM_LANGS_COL, 2)
        self._to_langs = self._root.add_collection(TO_LANGS_COL)
        self._words = self._root.add_collection(WORDS_COL)

        self._non_translation_flags = self._root.add_collection(CONFS_COL)

    def _configure_collections(self) -> None:
        self._configure_translation_collections()
        self._configure_non_translation_flags_collection()

    def _configure_translation_collections(self) -> None:
        self._current_modes.set_type(str)
        self._current_modes.set_get_default(Configurations.get_default_translation_mode)
        self._from_langs.set_get_default(lambda: Configurations.get_nth_saved_language(0, *self._to_langs))
        self._to_langs.add_get_default_if_or(lambda: Configurations.get_nth_saved_language(1, *self._from_langs), self._single_node.is_active, self._word_node.is_active)
        self._to_langs.add_get_default_if_or(lambda: list(Configurations.load_config_languages_by_limit(*self._from_langs)), self._lang_node.is_active, self._double_multi_node.is_active)

    def _configure_non_translation_flags_collection(self) -> None:
        existing = filter(self.root.has_flag, chain(just_set, just_display, display_with_arg, other_config))
        flags = map(self._root.get_flag, existing)
        unique_flags = unique_everseen(flags, Flag.get_name)
        self._non_translation_flags.add_to_add_self(*list(unique_flags))

    def _create_flags(self) -> None:
        self._create_mode_flags()
        self._create_configurational_flags()
        self._create_functional_flags()

    def _create_mode_flags(self) -> None:
        self._single_flag = self._root.add_flag(F.M.SINGLE_LONG_FLAG, F.M.SINGLE_SHORT_FLAG)
        self._lang_flag = self._root.add_flag(F.M.LANG_LONG_FLAG, F.M.LANG_SHORT_FLAG)
        self._word_flag = self._root.add_flag(F.M.WORD_LONG_FLAG, F.M.WORD_SHORT_FLAG)

    def _create_configurational_flags(self) -> None:
        self.root.add_flag(F.C.LANG_LIMIT_LONG_FLAG, F.C.LANG_LIMIT_SHORT_FLAG, flag_lower_limit=0, flag_limit=1)
        self.root.add_flag(F.C.LANGS_SHOW_LONG_FLAG, F.C.LANGS_SHOW_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(F.C.LAST_LANG_LONG_FLAG, flag_lower_limit=1, flag_limit=1)
        self.root.add_flag(F.C.LAST_1_LONG_FLAG, F.C.LAST_1_SHORT_FLAG, storage_limit=0, default=1)
        self.root.add_flag(F.C.LAST_2_LONG_FLAG, F.C.LAST_2_SHORT_FLAG, storage_limit=0, default=2)
        self.root.add_flag(F.C.DEFAULT_MODE_LONG_FLAG, F.C.DEFAULT_MODE_SHORT_FLAG, flag_lower_limit=0, flag_limit=1)
        self.root.add_flag(F.C.SETTINGS_LONG_FLAG, F.C.SETTINGS_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(F.C.ADD_LANG_LONG_FLAG, F.C.ADD_LANG_SHORT_FLAG, flag_lower_limit=1, flag_limit=None)
        self.root.add_flag(F.C.REMOVE_LANG_LONG_FLAG, F.C.REMOVE_LANG_SHORT_FLAG, flag_lower_limit=1, flag_limit=None)
        self.root.add_flag(F.C.DOUBLE_MODE_STYLE_LONG_FLAG, F.C.DOUBLE_MODE_STYLE_SHORT_FLAG, flag_limit=1)
        self.root.add_flag(F.C.LAYOUT_ADJUSTMENT_METHOD_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_METHOD_SHORT_FLAG, flag_limit=1)
        self.root.add_flag(F.C.LAYOUT_ADJUSTMENT_LANG_LONG_FLAG, F.C.LAYOUT_ADJUSTMENT_LANG_SHORT_FLAG, flag_limit=1)

    def _create_functional_flags(self) -> None:
        self.root.add_flag(F.F.SILENT_LONG_FLAG, flag_limit=0)
        self.root.add_flag(F.F.REVERSE_LONG_FLAG, F.F.REVERSE_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(F.F.SYNOPSIS_LONG_FLAG, F.F.SYNOPSIS_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(F.F.FROM_LANG_LONG_FLAG, F.F.FROM_LANG_SHORT_FLAG, flag_limit=1, storage=self._from_langs)
        self._conjugation_flag = self.root.add_flag(F.F.CONJUGATION_LONG_FLAG, F.F.CONJUGATION_SHORT_FLAG, F.F.CONJUGATION_SUPER_SHORT_FLAG, flag_limit=0)
        self._cconjugation_flag = self.root.add_flag(F.F.CCONJUGATION_LONG_FLAG, F.F.CCONJUGATION_SHORT_FLAG, F.F.CCONJUGATION_SUPER_SHORT_FLAG, flag_limit=0)

    def _configure_flags(self) -> None:
        self._configure_mode_flags()
        self._configure_configuration_flags()
        self._configure_functional_flags()

    def _configure_mode_flags(self) -> None:
        self._current_modes.add_to_add_names(self._single_flag, self._lang_flag, self._word_flag, self._conjugation_flag)
        self._word_flag.set_limit(None, storage=self._words)  # infinite
        self._lang_flag.set_limit(None, storage=self._to_langs)  # infinite

    def _configure_configuration_flags(self) -> None:
        self._root.get_flag(F.C.LANG_LIMIT_LONG_FLAG).set_type(int)
        self._root.get_flag(F.C.LAST_LANG_LONG_FLAG).set_type(int)
        self._root.get_flag(F.C.LAST_LANG_LONG_FLAG).set_get_default(Configurations.get_from_language)
        self.root.get_flag(F.C.DOUBLE_MODE_STYLE_LONG_FLAG).set_get_default(lambda: Configurations.get_conf(F.C.DOUBLE_MODE_STYLE_LONG_FLAG))
        self.root.get_flag(F.C.LAYOUT_ADJUSTMENT_METHOD_LONG_FLAG).set_get_default(Configurations.get_adjustment_method)
        self.root.get_flag(F.C.LAYOUT_ADJUSTMENT_LANG_LONG_FLAG).set_get_default(Configurations.get_adjustment_lang)

    def _configure_functional_flags(self) -> None:
        self.root.get_flag(F.F.SILENT_LONG_FLAG).when_active(lambda: TranslationPrinter.turn(False))
        self.root.get_flag(F.F.SYNOPSIS_LONG_FLAG).when_active(lambda: TranslationPrinter.out(self.root.help.synopsis))

    def _create_params(self) -> None:
        self._to_langs_param = Parameter('to_langs', parameter_lower_limit=0, parameter_limit=None)
        self._words_param = Parameter('words', parameter_lower_limit=1, parameter_limit=None)
        self._configuration_args = Parameter('conf_args', storage_lower_limit=0, storage_limit=None)

    def _create_hidden_nodes(self) -> None:
        self.root.set_only_hidden_nodes()
        self._create_translation_nodes()
        self._create_configuration_node()
        self._create_display_node()

    def _create_translation_nodes(self) -> None:
        self._translation_node = self.root.add_hidden_node('trans')
        self._single_node = self._translation_node.add_hidden_node(TranslationTypes.SINGLE, action=self._translate_single)
        self._lang_node = self._translation_node.add_hidden_node(TranslationTypes.LANG, action=self._translate_multi_lang)
        self._word_node = self._translation_node.add_hidden_node(TranslationTypes.WORD, action=self._translate_multi_word)
        self._double_multi_node = self._translation_node.add_hidden_node(TranslationTypes.DOUBLE, action=self._translate_double)
        self._conjugation_node = self._translation_node.add_hidden_node(TranslationTypes.CONJ, action=self._get_conjugation)

    def _create_configuration_node(self) -> None:
        self._configuration_node = self.root.add_hidden_node('conf')

    def _create_display_node(self) -> None:
        self._display_node = self.root.add_hidden_node('display')

    def _configure_hidden_nodes(self) -> None:
        self._configure_translation_nodes()
        self._configure_configuration_node()
        self._configure_display_node()

    def _configure_translation_nodes(self) -> None:
        self._configure_main_translation_node()
        self._configure_single_node()
        self._configure_lang_node()
        self._configure_word_node()
        self._configure_double_node()
        self._configure_conjugation_node()

    def _configure_main_translation_node(self) -> None:
        self._translation_node.set_only_hidden_nodes()
        self._translation_node.set_active(self._configuration_node.is_inactive, self._display_node.is_inactive, but_not=(lambda: self.root.get_flag(F.HELP_LONG_FLAG).is_active(),))
        # self._translation_node.set_inactive_on_conditions(lambda: not len(self._args))

    def _configure_single_node(self) -> None:
        self._single_node.set_active_on_flags_in_collection(self._current_modes, self._single_flag, self._conjugation_flag, func=any, but_not=[self._word_flag, self._lang_flag])
        self.add_post_flag_parsing_action_when(
            lambda: self._single_node.set_inactive_and(lambda: True),
            lambda: (self._conjugation_flag.is_active() or self._cconjugation_flag.is_active()) and self._used_arity <= 2
        )

        self._single_node.set_params('word', 'from_lang', 'to_lang', storages=(self._words, self._from_langs, self._to_langs))
        self._single_node.set_possible_param_order('word from_lang to_lang')
        self._single_node.set_possible_param_order('word to_lang')
        self._single_node.set_possible_param_order('word')

    def _configure_cli(self) -> None:
        self.when_used_arity_is_equal(lambda: self._word_node.disable_order(2), 2)
        self.add_post_parse_action_when(self._reverse_langs, lambda: self.root.get_flag(F.F.REVERSE_SHORT_FLAG).is_active() and self._single_node.is_active())

    def _reverse_langs(self):
        from_langs = self._from_langs[:]
        self._from_langs.reset()
        self._from_langs += self._to_langs
        self._to_langs.reset()
        self._to_langs += from_langs

    def _cli_translate(self):
        # TODO: fix reverse mode for single
        return self._scrapper.scrap_translation(from_lang=self._from_langs.get(), to_langs=self._to_langs.get_as_list(), words=self._words.get_as_list())

    def _translate_single(self) -> None:  # TODO: write a test for conj in single
        if self._conjugation_flag.is_inactive():
            return self._translate(self._cli_translate, prefix_style=TranslationTypes.SINGLE)
        else:
            self._correct_misplaced()
            result = self._scrapper.scrap_translation_and_conjugation(from_lang=self._from_langs.get(), to_lang=self._to_langs.get(), word=self._words.get())
            translations = next(result)
            TranslationPrinter.print_with_formatting(translations, prefix_style=TranslationTypes.SINGLE)
            conjugations = next(result)
            self._print_conjugations(conjugations)
            return translations

    def _translate_multi_lang(self) -> None:
        return self._translate(self._cli_translate, prefix_style=TranslationTypes.LANG)

    def _translate_multi_word(self) -> None:
        return self._translate(self._cli_translate, prefix_style=TranslationTypes.WORD)

    def _translate_double(self) -> None:
        main_division = self.root.get_flag(F.C.DOUBLE_MODE_STYLE_LONG_FLAG).get()
        prefix_style = self._get_prefix_style_for_main_division(main_division)
        translations = self._translate(self._cli_translate, prefix_style=prefix_style, main_division=main_division)
        return translations

    def _get_conjugation(self) -> None:
        tables = self._scrapper.scrap_conjugation(self._from_langs.get(), self._words.get())  # Check if it's being parsed well
        self._print_conjugations(tables)

    def _print_conjugations(self, tables: Iterable) -> None:
        filtered = self._filter_unnecessary_tables(tables)
        formatted = TableFormatter.format_many(filtered)
        string = TableFormatter.format_many_into_string(formatted, sep='\n\n')
        TranslationPrinter.out(string)

    # TODO: test
    def _filter_unnecessary_tables(self, tables: Iterable[DataFrame]) -> Iterable[DataFrame]:
        if self._conjugation_flag.is_active():
            return islice(tables, 1)
        tables_instances = list(tables)
        length = len(tables_instances)
        if length > 1:
            return tables_instances[length//2:]
        return tables_instances

    def _get_prefix_style_for_main_division(self, main_division: TranslationTypes) -> TranslationTypes:
        match main_division:
            case TranslationTypes.LANG:
                return TranslationTypes.WORD
            case TranslationTypes.WORD:
                return TranslationTypes.LANG
            case _:
                return TranslationTypes.DOUBLE

    def _translate(self, translate: Callable[[], Iterable[TranslationResult]], *, prefix_style: TranslationTypes, main_division: TranslationTypes = None) -> None | Iterable[TranslationResult]:
        self._correct_misplaced()
        if self._is_translating:
            translation = translate()
            TranslationPrinter.print_with_formatting(translation, prefix_style=prefix_style, main_division=main_division)
            return translation

    def _configure_lang_node(self) -> None:
        self._lang_node.set_active_on_flags_in_collection(self._current_modes, self._lang_flag, but_not=self._word_flag)

        self._lang_node.set_params('word', 'from_lang', self._to_langs_param, storages=(self._words, self._from_langs, self._to_langs))
        self._lang_node.get_param('to_langs').set_to_multi_at_least_zero()
        self._lang_node.set_possible_param_order('word from_lang to_langs')
        self._lang_node.set_possible_param_order('word')

    def _configure_word_node(self) -> None:
        self._word_node.set_active_on_flags_in_collection(self._current_modes, self._word_flag, but_not=[self._lang_flag, self._single_flag])

        self._word_node.set_params('from_lang', 'to_lang', self._words_param, storages=(self._from_langs, self._to_langs, self._words))
        self._word_node.set_possible_param_order('from_lang to_lang words')
        self._word_node.set_possible_param_order('to_lang words')
        self._word_node.set_possible_param_order('to_lang')
        self._word_node.set_parameters_to_skip_order('words')

    def _configure_double_node(self) -> None:
        self._double_multi_node.set_active_on_flags_in_collection(self._current_modes, self._lang_flag, self._word_flag, but_not=self._single_flag)

        self._double_multi_node.set_params('word', 'from_lang', 'to_langs', storages=(self._words, self._from_langs, self._to_langs))
        self._double_multi_node.set_possible_param_order('from_lang')
        self._double_multi_node.set_possible_param_order('')

    def _configure_conjugation_node(self) -> None:
        self._conjugation_node.set_active_or(
            lambda: self._conjugation_flag.is_active() and self._single_node.is_inactive(),
            lambda: self._cconjugation_flag.is_active() and self._single_node.is_inactive()
        )
        self._conjugation_node.set_params('word', 'lang', storages=(self._words, self._from_langs))

    # TODO: add information printing after setting a conf
    # TODO: add possible values checking (also in smartcli)
    def _configure_configuration_node(self) -> None:
        self._configuration_node.add_param(self._configuration_args)
        self._configuration_node.set_active_and(lambda: len(self._non_translation_flags) > 0,
                                                lambda: all(len(storage) > 0 for storage in map(Flag.get_storage, self._non_translation_flags.get_plain())))
        self._configuration_node.set_inactive_on_conditions(lambda: any(flag.name in display_with_arg for flag in self._non_translation_flags))

        self._configure_simple_setting_options()
        self._configure_add_lang_option()
        self._configure_remove_lang_option()
        self._configure_default_mode_option()

    def _configure_simple_setting_options(self) -> None:
        self._configuration_node.add_action(lambda: self._set_flag_confs(*list(filter(lambda flag: flag.has_name_in(just_set), self._non_translation_flags))))

    def _configure_add_lang_option(self) -> None:
        add_lang_flag = self._root.get_flag(F.C.ADD_LANG_LONG_FLAG)
        self._configuration_node.add_action_when_is_active(lambda: Configurations.add_langs(*add_lang_flag.get_plain()), add_lang_flag)

    def _configure_remove_lang_option(self) -> None:
        remove_lang_flag = self._root.get_flag(F.C.REMOVE_LANG_SHORT_FLAG)
        self._configuration_node.add_action_when_is_active(lambda: Configurations.remove_langs(*remove_lang_flag.get_plain()), remove_lang_flag)

    def _configure_default_mode_option(self) -> None:
        default_mode_flag = self.root.get_flag(F.C.DEFAULT_MODE_LONG_FLAG)
        set_conf = lambda: Configurations.set_conf(default_mode_flag.name, self.root.get_flag(self._to_flag(default_mode_flag.get())).name)
        self._configuration_node.add_action_when_is_active(set_conf, default_mode_flag)

    def _set_flag_confs(self, *flags: Flag) -> None:
        for flag in flags:
            Configurations.set_conf(flag.name, flag.get())

    def _to_flag(self, to_flag: str) -> str:
        return f'-{to_flag}' if len(to_flag) < 3 else f'--{to_flag}'

    def _configure_display_node(self) -> None:
        self._display_node.set_active(lambda: len(self._non_translation_flags) > 0,
                                      lambda: all(len(flag.get_storage()) == 0 or (flag.name in display_with_arg and len(flag.get_storage()) > 0) for flag in self._non_translation_flags.get_plain()))

        self._display_node.add_action(lambda: list(map(lambda conf: ConfigDisplayer.display_config(conf), map(Flag.get_name, filter(lambda flag: flag.has_name_in(just_display), self._non_translation_flags)))))
        self._display_node.add_action(lambda: list(map(lambda conf: ConfigDisplayer.display_possible_values(conf), map(Flag.get_name, filter(lambda flag: flag.has_name_in(just_display), self._non_translation_flags)))))
        self._display_node.add_action_when_is_active_or(self._display_nth_last_lang, *self.root.get_flags(F.C.LAST_LANG_LONG_FLAG, F.C.LAST_1_LONG_FLAG, F.C.LAST_2_LONG_FLAG))
        self._display_node.add_action_when_is_active(self._display_settings, self.root.get_flag(F.C.SETTINGS_LONG_FLAG))

    def _display_nth_last_lang(self):
        active = next(filter(Flag.is_active, self._non_translation_flags))
        lang_nums = map(lambda num: num - 1, active.get_as_list())
        nth_lang = map(Configurations.get_nth_saved_language, lang_nums)
        ConfigDisplayer.display_config(active.name, list(nth_lang))

    def _display_settings(self):
        configs = Configurations.get_all_configs()
        ConfigDisplayer.display_configs(**configs)

    def set_out_stream(self, out):
        super().set_out_stream(out)
        ConfigDisplayer.out_func = out
        TranslationPrinter.out_func = out

    def _correct_misplaced(self):
        '''
            How and why exactly the nested if exists is not clear to me
            Until a better explanation I announce it magic
        '''
        if self._word_filter.is_any_lang_misplaced(*self._from_langs, *self._to_langs):
            from_langs, to_langs, words = self._word_filter.split_from_from_and_to_langs(self._from_langs, self._to_langs)
            self._from_langs.reset()
            self._from_langs += from_langs
            self._to_langs.reset()
            self._to_langs += to_langs
            self._words += words

            if self._word_filter.is_any_word_moved_from_to_langs():
                if self._single_node.is_active():
                    self._from_langs += -self._words
                self._to_langs += -self._from_langs

            if self._word_filter.is_any_word_moved_from_from_langs() and not self._word_node.is_active():
                self._from_langs += -self._words

            self._word_filter.reset()

    def _add_translation_args_preprocessing_actions(self) -> None:
        self.add_args_preprocessing_action(self._adjust_args, lambda: Configurations.get_adjustment_method() in LayoutAdjustmentsMethods.get_adjusting_methods())

    def _adjust_args(self, args: list[str]) -> list[str]:
        method = Configurations.get_adjustment_method()
        lang = Configurations.get_adjustment_lang()
        adjuster = LayoutAdjusterFactory.get_layout_adjuster(method, lang)
        return [adjuster.adjust(arg) for arg in args]

    def _create_help(self) -> None:
        self.root.add_general_help_flag_to_all(F.HELP_LONG_FLAG, F.HELP_SHORT_FLAG)
        self._create_translation_nodes_help()

    def _create_translation_nodes_help(self) -> None:
        self._single_node.help.short_description = 'Translates one word from and to one language'
        self._single_node.help.long_description = ''
        self._single_node.help.synopsis = 'trans <WORD> [FROM_LANG] [TO_LANG]'
        self._word_node.help.short_description = 'Translates many words from one language and to one language'
        self._word_node.help.long_description = ''
        self._word_node.help.synopsis = 'trans [FROM_LANG] [TO_LANG] [-w] <WORD>...'
        self._lang_node.help.short_description = 'Translates a word from a single language to many languages'
        self._lang_node.help.short_description = ''
        self._lang_node.help.synopsis = 'trans <WORD> [FROM_LANG] [-m] <TO_LANG>...'
        self._double_multi_node.help.short_description = 'Translates many words from a single language into many languages'
        self._double_multi_node.help.long_description = ''
        self._double_multi_node.help.synopsis = 'trans [FROM_LANG] -w <WORD>... -m <TO_LANG>... '

        self.root.help.name = 'trans'
        self.root.help.short_description = 'Translation program'
        self.root.help.long_description = ''\
            'The translator allows to translate a word from and to every language supported by Glosbe translator (glosbe.com). '\
            'The program has single mode that allows to perform a single translation (one word from one language to one language); '\
            'multi-lang mode that allows to translate a word from one language into multiple languages; '\
            'multi-word mode that allows to translate many words into and from one language and also'\
            'double mode that allows to translate many words into many languages from a selected language.'
        self.root.help.synopsis = ''\
            + f'{self._single_node.name}: {self._single_node.help.synopsis}\n'\
            + f'{self._lang_node.name}: {self._lang_node.help.synopsis}\n'\
            + f'{self._word_node.name}: {self._word_node.help.synopsis}\n'\
            + f'{self._double_multi_node.name}: {self._double_multi_node.help.synopsis}'