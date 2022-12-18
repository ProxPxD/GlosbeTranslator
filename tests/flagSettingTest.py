from parameterized import parameterized
from smartcli.nodes.smartList import SmartList

from src.glosbe.configurations import Configurations
from src.glosbe.translatorCli import SINGLE_LONG_FLAG, DEFAULT_MODE_SHORT_FLAG, DEFAULT_MODE_LONG_FLAG, LANG_LIMIT_SHORT_FLAG, LANG_LIMIT_LONG_FLAG, \
	LANG_LONG_FLAG, WORD_LONG_FLAG, LANGS_SHOW_LONG_FLAG, LANGS_SHOW_SHORT_FLAG, LAST_LANG_LONG_FLAG, LAST_2_SHORT_FLAG, LAST_2_LONG_FLAG, LAST_1_SHORT_FLAG, \
	LAST_1_LONG_FLAG, SETTINGS_SHORT_FLAG, SETTINGS_LONG_FLAG, ADD_LANG_SHORT_FLAG, ADD_LANG_LONG_FLAG, REMOVE_LANG_LONG_FLAG, REMOVE_LANG_SHORT_FLAG
from src.translate import get_default_configs
from tests.abstractCliTest import AbstractCliTest


class FlagSettingTest(AbstractCliTest):

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Flag Setting'

	def get_file_name(self) -> str:
		return 'flag_test'

	def setUp(self) -> None:
		super().setUp()
		Configurations.init(self.get_file_name(), default=get_default_configs())

	def tearDown(self) -> None:
		super().tearDown()
		Configurations.remove_current_configuration()

	@parameterized.expand([
		('short_limit', LANG_LIMIT_SHORT_FLAG, LANG_LIMIT_LONG_FLAG, 3, [3]),
		('long_limit', LANG_LIMIT_LONG_FLAG, LANG_LIMIT_LONG_FLAG, 1, [1]),
		('short_default_mode_original', DEFAULT_MODE_SHORT_FLAG, DEFAULT_MODE_LONG_FLAG, SINGLE_LONG_FLAG, ['single']),
		('long_default_mode_original', DEFAULT_MODE_LONG_FLAG, DEFAULT_MODE_LONG_FLAG, LANG_LONG_FLAG, ['lang']),
		('short_default_mode_with_change', DEFAULT_MODE_SHORT_FLAG, DEFAULT_MODE_LONG_FLAG, WORD_LONG_FLAG, ['w']),
		('long_default_mode_with_change', DEFAULT_MODE_LONG_FLAG, DEFAULT_MODE_LONG_FLAG, LANG_LONG_FLAG, ['m']),
	])
	def test_set_configuration(self, name: str, flag: str, conf_to_get: str, expected, flag_args: list[str]):
		self.cli.parse(f't {flag} {" ".join(map(str, flag_args))}')
		conf_value = Configurations.get_conf(conf_to_get)
		self.assertEqual(expected, conf_value)

	@parameterized.expand([
		('short_limit', LANG_LIMIT_SHORT_FLAG, LANG_LIMIT_LONG_FLAG, [3]),
		('long_limit', LANG_LIMIT_LONG_FLAG, LANG_LIMIT_LONG_FLAG, [1]),
		('short_default_mode_original', DEFAULT_MODE_SHORT_FLAG, DEFAULT_MODE_LONG_FLAG, [SINGLE_LONG_FLAG]),
		('long_default_mode_original', DEFAULT_MODE_LONG_FLAG, DEFAULT_MODE_LONG_FLAG, [LANG_LONG_FLAG]),
		('short_default_mode_with_change', DEFAULT_MODE_SHORT_FLAG, DEFAULT_MODE_LONG_FLAG, [WORD_LONG_FLAG]),
		('long_default_mode_with_change', DEFAULT_MODE_LONG_FLAG, DEFAULT_MODE_LONG_FLAG, [LANG_LONG_FLAG]),
		('short_langs', LANGS_SHOW_SHORT_FLAG, LANGS_SHOW_LONG_FLAG, ['pl', 'es', 'de']),
		('long_langs', LANGS_SHOW_LONG_FLAG, LANGS_SHOW_LONG_FLAG, ['pl', 'es', 'de']),
	])
	def test_display_configuration(self, name: str, flag: str, conf_to_set: str, to_saves: list[str]):
		to_save = to_saves[0] if len(to_saves) == 1 else to_saves
		if to_save:
			Configurations.set_conf(conf_to_set, to_save)
		text = SmartList()

		self.cli.set_out_stream(text.__iadd__)
		self.cli.parse(f't {flag}')
		text = '\n'.join(text)
		expected_ending = ', '.join(to_save) if 'langs' in name else str(to_save)
		self.assertTrue(text.endswith(expected_ending))

	@parameterized.expand([
		('last_1st', LAST_LANG_LONG_FLAG, [1], 0),
		('last_3rd', LAST_LANG_LONG_FLAG, [3], 2),
		('long_last_first', LAST_1_LONG_FLAG, [], 0),
		('short_last_first', LAST_1_SHORT_FLAG, [], 0),
		('long_last_second', LAST_2_LONG_FLAG, [], 1),
		('short_last_second', LAST_2_SHORT_FLAG, [], 1),

	])
	def test_display_last_language(self, name: str, flag: str, flag_args: list[str], lang_to_take: int):
		Configurations.set_conf(LANGS_SHOW_LONG_FLAG, ['pl', 'es', 'zh', 'de'])
		text = SmartList()
		self.cli.set_out_stream(text.__iadd__)

		self.cli.parse(f't {flag} {" ".join(map(str, flag_args))}')

		actual_lang = '\n'.join(text).split(' ')[-1]
		expected_lang = Configurations.get_nth_saved_language(lang_to_take)
		self.assertEqual(expected_lang, actual_lang)

	@parameterized.expand([
		('long_flag', ADD_LANG_LONG_FLAG, 'pl'),
		('short_flag', ADD_LANG_SHORT_FLAG, 'de'),
	])
	def test_add_language(self, name, command: str, lang: str):
		self.cli.parse(f't {command} {lang}')
		langs = Configurations.get_saved_languages()
		self.assertIn(f'{lang}', langs)

	@parameterized.expand([
		('long_flag', REMOVE_LANG_LONG_FLAG, 'pl'),
		('short_flag', REMOVE_LANG_SHORT_FLAG, 'de'),
	])
	def test_remove_language(self, name, command: str, lang: str):
		Configurations.add_langs(lang)
		self.cli.parse(f't {command} {lang}')
		langs = Configurations.get_saved_languages()
		self.assertNotIn(f'{lang}', langs)

	@parameterized.expand([
		('long_settings', SETTINGS_LONG_FLAG),
		('short_settings', SETTINGS_SHORT_FLAG),
	])
	def test_display_settings(self, name, flag):
		text = SmartList()
		self.cli.set_out_stream(text.__iadd__)

		self.cli.parse(f't {flag}')

		printed_keys = list(map(lambda t: f'--{t.split(":")[0]}', text))
		configs = list(Configurations.get_all_configs().keys())

		self.assertEqual(configs, printed_keys)

	def test_add_multiple_langs(self):
		Configurations.add_langs('pl')
		self.cli.parse('t -al pl pl pl pl pl')

		self.assertEqual(1, len(list(filter(lambda l: l == 'pl', Configurations.get_saved_languages()))))