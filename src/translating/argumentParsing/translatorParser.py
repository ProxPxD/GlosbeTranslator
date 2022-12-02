from smartcli import Cli, Root, CliCollection, Flag, VisibleNode

from ..configs.configurations import Configurations
from ..translatingPrinting.translationPrinter import TranslationPrinter
from ..translator import Translator, TranslationTypes


class TranslatorCli(Cli):

    def __init__(self, args: list[str] = None):
        super().__init__(args=args)
        self._current_modes: CliCollection
        self._from_langs: CliCollection
        self._to_langs: CliCollection
        self._words: CliCollection
        self._single_node: VisibleNode
        self._word_node: VisibleNode
        self._lang_node: VisibleNode
        self._double_multi_node: VisibleNode
        self._from_langs: Flag
        self._to_langs: Flag
        self._words: Flag

        self._translator = Translator()
        self._translation_printer = TranslationPrinter()

        self._root = Root('root')
        self._create_collections()
        self._create_flags()
        self._create_hidden_nodes()

        self._configure_collections()
        self._configure_flags()
        self._configure_hidden_nodes()

    def _create_collections(self) -> None:
        self._current_modes = self._root.add_collection('current_modes')
        self._current_modes.set_type(str)
        self._current_modes.set_get_default(Configurations.get_default_translation_mode)
        self._from_langs = self._root.add_collection('from_langs', 1)
        self._from_langs.set_get_default(Configurations.get_from_language)
        self._to_langs = self._root.add_collection('to_langs')

    def _configure_collections(self) -> None:
        self._to_langs.add_get_default_if_or(lambda: Configurations.get_nth_saved_language(1, *self._from_langs), self._single_node.is_active,
                                             self._word_node.is_active)
        self._to_langs.add_get_default_if_or(lambda: Configurations.load_config_languages(*self._from_langs), self._lang_node.is_active,
                                             self._double_multi_node.is_active)
        self._words = self._root.add_collection('words')

    def _create_flags(self) -> None:
        self._single_flag = self._root.add_flag('--single', '-s')
        self._lang_flag = self._root.add_flag('--multi', '-m')
        self._word_flag = self._root.add_flag('--word', '-w')

    def _configure_flags(self) -> None:
        self._current_modes.add_to_add_names(self._single_flag, self._lang_flag, self._word_flag)
        self._word_flag.set_limit(None, storage=self._words)  # infinite
        self._lang_flag.set_limit(None, storage=self._to_langs)  # infinite

    def _create_hidden_nodes(self) -> None:
        self.root.set_only_hidden_nodes()
        self._single_node = self._root.add_hidden_node(TranslationTypes.SINGLE, action=self.translate_single)
        self._lang_node = self._root.add_hidden_node(TranslationTypes.LANG, action=lambda: None)
        self._word_node = self._root.add_hidden_node(TranslationTypes.WORD, action=lambda: None)
        self._double_multi_node = self._root.add_hidden_node(TranslationTypes.DOUBLE, action=lambda: None)

    def _configure_hidden_nodes(self) -> None:
        self._configure_single_node()
        self._configure_lang_node()
        self._configure_word_node()
        self._configure_double_node()

    def _configure_single_node(self) -> None:
        self._single_node.set_active_on_flags_in_collection(self._current_modes, self._single_flag, but_not=[self._word_flag, self._lang_flag])

        self._single_node.set_params('word', 'from_lang', 'to_lang', storages=(self._words, self._from_langs, self._to_langs))
        self._single_node.set_possible_param_order('word from_lang to_lang')
        self._single_node.set_possible_param_order('word to_lang')
        self._single_node.set_possible_param_order('word')

    def translate_single(self) -> None:
        translation = self._translator.single_translate(word=self._words.get(), to_lang=self.to_langs.get(), from_lang=self.from_lang.get())
        TranslationPrinter.print_translations(translation)

    def _configure_lang_node(self) -> None:
        self._lang_node.set_active_on_flags_in_collection(self._current_modes, self._lang_flag, but_not=self._word_flag)

        self._lang_node.set_params('word', 'from_lang', 'to_langs', storages=(self._words, self._from_langs, self._to_langs))
        self._lang_node.set_possible_param_order('words from_lang to_langs')
        self._lang_node.set_default_setting_order('from_lang')

    def _configure_word_node(self) -> None:
        self._word_node.set_active_on_flags_in_collection(self._current_modes, self._word_flag, but_not=[self._lang_flag, self._single_flag])

        self._word_node.set_params('word', 'from_lang', 'to_langs', storages=(self._words, self._from_langs, self._to_langs))
        self._word_node.set_possible_param_order('from_lang to_langs words')
        self._lang_node.set_default_setting_order('from_lang', 'to_langs')

    def _configure_double_node(self) -> None:
        self._double_multi_node.set_active_on_flags_in_collection(self._current_modes, self._lang_flag, self._word_flag, but_not=self._single_flag)

        self._double_multi_node.set_params('word', 'from_lang', 'to_langs', storages=(self._words, self._from_langs, self._to_langs))
        self._double_multi_node.set_possible_param_order('from_lang')
        self._double_multi_node.set_possible_param_order('')

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

    def _correct_misplaced(self):
        if self._word_filter.is_any_lang_misplaced(*self._from_lang, *self._to_langs):
            self._from_lang, self._to_langs, words = self._word_filter.split_from_from_and_to_langs(self._from_lang, self.to_langs)
            self._words += words
            if self._is_to_lang_in_from_lang():
                self._to_langs += -self._from_lang
            if self._is_from_lang_in_words():
                self._from_lang += -self.words