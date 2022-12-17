from itertools import chain
from typing import Callable, Iterable

from more_itertools import unique_everseen
from smartcli import Parameter, HiddenNode, Cli, Root, CliCollection, Flag

from .wordFilter import WordFilter
from ..configs.configDisplayer import ConfigDisplayer
from ..configs.configurations import Configurations
from ..translatingPrinting.translationPrinter import TranslationPrinter
from ..translator import Translator, TranslationTypes, TranslationResult

CURRENT_MODES_COL = 'current_modes'
FROM_LANGS_COL = 'from_langs'
TO_LANGS_COL = 'to_langs'
WORDS_COL = 'words'
CONFS_COL = 'configurations'

# Modes
SINGLE_LONG_FLAG = '--single'
LANG_LONG_FLAG = '--lang'
WORD_LONG_FLAG = '--word'
SINGLE_SHORT_FLAG = '-s'
LANG_SHORT_FLAG = '-m'
WORD_SHORT_FLAG = '-w'

# Flags:
LANG_LIMIT_LONG_FLAG = '--limit'
LANG_LIMIT_SHORT_FLAG = '-l'
LANGS_SHOW_LONG_FLAG = '--langs'
LANGS_SHOW_SHORT_FLAG = '-ll'
LAST_LANG_LONG_FLAG = '--last'  # put number
LAST_1_LONG_FLAG = '--last1'
LAST_1_SHORT_FLAG = '-1'
LAST_2_LONG_FLAG = '--last2'
LAST_2_SHORT_FLAG = '-2'
DEFAULT_MODE_LONG_FLAG = '--default-mode'
DEFAULT_MODE_SHORT_FLAG = '-dm'
SETTINGS_LONG_FLAG = '--settings'
SETTINGS_SHORT_FLAG = '-ss'
HELP_LONG_FLAG = '--help'
HELP_SHORT_FLAG = '-h'

# Flags of nodes
ADD_LANG_LONG_FLAG = '--add-lang'
ADD_LANG_SHORT_FLAG = '-al'
REMOVE_LANG_LONG_FLAG = '--remove-lang'
REMOVE_LANG_SHORT_FLAG = '-rl'

just_set = (LANG_LIMIT_LONG_FLAG, )
just_display = (LANG_LIMIT_LONG_FLAG, DEFAULT_MODE_LONG_FLAG, LANGS_SHOW_LONG_FLAG, )
display_with_arg = (LAST_LANG_LONG_FLAG, )
other_config = (LAST_1_LONG_FLAG, LAST_2_LONG_FLAG, ADD_LANG_LONG_FLAG, REMOVE_LANG_LONG_FLAG, SETTINGS_LONG_FLAG)

modes = (SINGLE_LONG_FLAG, LANG_LONG_FLAG, WORD_LONG_FLAG)


class TranslatorCli(Cli):

    def __init__(self, args: list[str] = None):
        super().__init__(args=args)
        self._current_modes: CliCollection
        self._from_langs: CliCollection
        self._to_langs: CliCollection
        self._words: CliCollection
        self._configuration_flags: CliCollection

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

        self._from_langs: Flag
        self._to_langs: Flag
        self._words: Flag

        self._translator = Translator()
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

        self._configuration_flags = self._root.add_collection(CONFS_COL)

    def _configure_collections(self) -> None:
        self._configure_translation_collections()
        self._configure_configuration_collections()

    def _configure_translation_collections(self) -> None:
        self._current_modes.set_type(str)
        self._current_modes.set_get_default(Configurations.get_default_translation_mode)
        self._from_langs.set_get_default(lambda: Configurations.get_nth_saved_language(0, *self._to_langs))
        self._to_langs.add_get_default_if_or(lambda: Configurations.get_nth_saved_language(1, *self._from_langs), self._single_node.is_active, self._word_node.is_active)
        self._to_langs.add_get_default_if_or(lambda: Configurations.load_config_languages(*self._from_langs), self._lang_node.is_active, self._double_multi_node.is_active)

    def _configure_configuration_collections(self) -> None:
        flags = unique_everseen(map(self._root.get_flag, chain(just_set, just_display, display_with_arg, other_config)))
        self._configuration_flags.add_to_add_self(*list(flags))

    def _create_flags(self) -> None:
        self._create_mode_flags()
        self._create_configurational_flags()

    def _create_mode_flags(self):
        self._single_flag = self._root.add_flag(SINGLE_LONG_FLAG, SINGLE_SHORT_FLAG)
        self._lang_flag = self._root.add_flag(LANG_LONG_FLAG, LANG_SHORT_FLAG)
        self._word_flag = self._root.add_flag(WORD_LONG_FLAG, WORD_SHORT_FLAG)

    def _create_configurational_flags(self):
        self.root.add_flag(LANG_LIMIT_LONG_FLAG, LANG_LIMIT_SHORT_FLAG, flag_lower_limit=0, flag_limit=1)
        self.root.add_flag(LANGS_SHOW_LONG_FLAG, LANGS_SHOW_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(LAST_LANG_LONG_FLAG, flag_lower_limit=1, flag_limit=1)
        self.root.add_flag(LAST_1_LONG_FLAG, LAST_1_SHORT_FLAG, storage_limit=0, default=1)
        self.root.add_flag(LAST_2_LONG_FLAG, LAST_2_SHORT_FLAG, storage_limit=0, default=2)
        self.root.add_flag(DEFAULT_MODE_LONG_FLAG, DEFAULT_MODE_SHORT_FLAG, flag_lower_limit=0, flag_limit=1)
        self.root.add_flag(SETTINGS_LONG_FLAG, SETTINGS_SHORT_FLAG, flag_limit=0)
        self.root.add_flag(ADD_LANG_SHORT_FLAG, ADD_LANG_LONG_FLAG, flag_lower_limit=1, flag_limit=None)
        self.root.add_flag(REMOVE_LANG_SHORT_FLAG, REMOVE_LANG_LONG_FLAG, flag_lower_limit=1, flag_limit=None)

    def _configure_flags(self) -> None:
        self._configure_mode_flags()
        self._configure_configuration_flags()

    def _configure_mode_flags(self) -> None:
        self._current_modes.add_to_add_names(self._single_flag, self._lang_flag, self._word_flag)
        self._word_flag.set_limit(None, storage=self._words)  # infinite
        self._lang_flag.set_limit(None, storage=self._to_langs)  # infinite

    def _configure_configuration_flags(self) -> None:
        self._root.get_flag(LANG_LIMIT_LONG_FLAG).set_type(int)
        self._root.get_flag(LAST_LANG_LONG_FLAG).set_type(int)
        self._root.get_flag(LAST_LANG_LONG_FLAG).set_get_default(Configurations.get_from_language)

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

    def _configure_main_translation_node(self) -> None:
        self._translation_node.set_only_hidden_nodes()
        self._translation_node.set_active_on_empty(self._configuration_flags)
        self._translation_node.set_inactive_on_conditions(lambda: not len(self._args))

    def _configure_single_node(self) -> None:
        self._single_node.set_active_on_flags_in_collection(self._current_modes, self._single_flag, but_not=[self._word_flag, self._lang_flag])

        self._single_node.set_params('word', 'from_lang', 'to_lang', storages=(self._words, self._from_langs, self._to_langs))
        self._single_node.set_possible_param_order('word from_lang to_lang')
        self._single_node.set_possible_param_order('word to_lang')
        self._single_node.set_possible_param_order('word')

    def _translate_single(self) -> None:
        self._translate(lambda: self._translator.single_translate(word=self._words.get(), to_lang=self._to_langs.get(), from_lang=self._from_langs.get()),
                        prefix_style=TranslationTypes.SINGLE)

    def _translate_multi_lang(self) -> None:
        self._translate(lambda: self._translator.multi_lang_translate(word=self._words.get(), to_langs=self._to_langs.get_as_list(), from_lang=self._from_langs.get()),
                        prefix_style=TranslationTypes.LANG)

    def _translate_multi_word(self) -> None:
        self._translate(lambda: self._translator.multi_word_translate(words=self._words.get_as_list(), to_lang=self._to_langs.get(), from_lang=self._from_langs.get()),
                        prefix_style=TranslationTypes.WORD)

    def _translate_double(self) -> None:
        self._translate(lambda: self._translator.double_multi_translate(words=self._words.get_as_list(), to_langs=self._to_langs.get_as_list(), from_lang=self._from_langs.get()),
                        prefix_style=TranslationTypes.DOUBLE,  #TODO: make prefix style and main division setable by the user with default values and flags
                        main_division=TranslationTypes.SINGLE) #TODO: remove empty dash content when prefix style is double and main division is single (joined style)

    def _translate(self, translate: Callable[[], Iterable[TranslationResult]], *, prefix_style: TranslationTypes, main_division: TranslationTypes = None) -> None:
        self._correct_misplaced()
        if self._is_translating:
            translation = translate()
            TranslationPrinter.print_with_formatting(translation, prefix_style=prefix_style, main_division=main_division)

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
        self.when_used_arity_is_equal(lambda: self._word_node.disable_order(2), 2)
        self._word_node.set_parameters_to_skip_order('words')

    def _configure_double_node(self) -> None:
        self._double_multi_node.set_active_on_flags_in_collection(self._current_modes, self._lang_flag, self._word_flag, but_not=self._single_flag)

        self._double_multi_node.set_params('word', 'from_lang', 'to_langs', storages=(self._words, self._from_langs, self._to_langs))
        self._double_multi_node.set_possible_param_order('from_lang')
        self._double_multi_node.set_possible_param_order('')

    # TODO: add information printing after setting a conf
    def _configure_configuration_node(self) -> None:
        self._configuration_node.add_param(self._configuration_args)
        self._configuration_node.set_active_and(lambda: len(self._configuration_flags) > 0,
                                                lambda: all(len(storage) > 0 for storage in map(Flag.get_storage, self._configuration_flags.get_plain())))
        self._configuration_node.set_inactive_on_conditions(lambda: any(flag.name in display_with_arg for flag in self._configuration_flags))

        self._configure_simple_setting_options()
        self._configure_add_lang_option()
        self._configure_remove_lang_option()
        self._configure_default_mode_option()

    def _configure_simple_setting_options(self) -> None:
        self._configuration_node.add_action(lambda: self._set_flag_confs(*list(filter(lambda flag: flag.has_name_in(just_set), self._configuration_flags))))

    def _configure_add_lang_option(self) -> None:
        add_lang_flag = self._root.get_flag(ADD_LANG_LONG_FLAG)
        self._configuration_node.add_action_when_is_active(lambda: Configurations.add_langs(*add_lang_flag.get_plain()), add_lang_flag)

    def _configure_remove_lang_option(self) -> None:
        remove_lang_flag = self._root.get_flag(REMOVE_LANG_SHORT_FLAG)
        self._configuration_node.add_action_when_is_active(lambda: Configurations.remove_langs(*remove_lang_flag.get_plain()), remove_lang_flag)

    def _configure_default_mode_option(self) -> None:
        default_mode_flag = self.root.get_flag(DEFAULT_MODE_LONG_FLAG)
        set_conf = lambda: Configurations.set_conf(default_mode_flag.name, self.root.get_flag(self._to_flag(default_mode_flag.get())).name)
        self._configuration_node.add_action_when_is_active(set_conf, default_mode_flag)

    def _set_flag_confs(self, *flags: Flag) -> None:
        for flag in flags:
            Configurations.set_conf(flag.name, flag.get())

    def _to_flag(self, to_flag: str) -> str:
        return f'-{to_flag}' if len(to_flag) < 3 else f'--{to_flag}'

    def _configure_display_node(self) -> None:
        self._display_node.set_active_and(lambda: len(self._configuration_flags) > 0,
                                          lambda: all(len(flag.get_storage()) == 0 or (flag.name in display_with_arg and len(flag.get_storage()) > 0) for flag in self._configuration_flags.get_plain()))

        self._display_node.add_action(lambda: list(map(lambda conf: ConfigDisplayer.display_config(conf), map(Flag.get_name, filter(lambda flag: flag.has_name_in(just_display), self._configuration_flags)))))
        self._display_node.add_action_when_is_active_or(self._display_nth_last_lang, *self.root.get_flags(LAST_LANG_LONG_FLAG, LAST_1_LONG_FLAG, LAST_2_LONG_FLAG))
        self._display_node.add_action_when_is_active(self._display_settings, self.root.get_flag(SETTINGS_LONG_FLAG))

    def _display_nth_last_lang(self):
        active = next(filter(Flag.is_active, self._configuration_flags))
        lang_nums = map(lambda num: num - 1, active.get_as_list())
        nth_lang = map(Configurations.get_nth_saved_language, lang_nums)
        ConfigDisplayer.display_config(active.name, list(nth_lang))

    def _display_settings(self):
        configs = Configurations.get_all_configs()
        ConfigDisplayer.display_configs(**configs)

    def set_out_stream(self, out):
        super().set_out_stream(out)
        ConfigDisplayer.out = out
        TranslationPrinter.out = out

    # TODO: refactor and remove the below

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