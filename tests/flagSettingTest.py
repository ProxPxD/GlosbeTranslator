from parameterized import parameterized

from src.translating.configs.configurations import Configurations
from tests.abstractCliTest import AbstractCliTest


class FlagSettingTest(AbstractCliTest):

	__file_name = 'flag_test'

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Flag Setting'

	def setUp(self) -> None:
		super().setUp()
		Configurations.init(self.__file_name)

	def tearDown(self) -> None:
		super().tearDown()
		Configurations.remove_current_configuration()

	@parameterized.expand([
		('short_limit', '-l', [3]),
		('long_limit', '--limit', [1]),
	])
	def test_setting_configuration(self, name: str, flag: str, flag_args: list[str]):
		self.cli.parse(f't {flag} {" ".join(map(str, flag_args))}')

		conf_value = Configurations.get_conf(flag)
		if not isinstance(conf_value, list):
			conf_value = [conf_value]

		self.assertEqual(conf_value, flag_args)

	@parameterized.expand([
		('short_limit', '-l', [3]),
		('long_limit', '--limit', [1]),
	])
	def test_getting_configuration(self, name: str, flag: str, flag_args: list[str]):
		arg = flag_args[0] if len(flag_args) == 1 else flag_args
		if arg:
			Configurations.set_conf(flag, arg)
		text = ''

		self.cli.set_out_stream(lambda result: text.replace('', result))
		self.cli.parse(f't {flag}')
		self.assertTrue(text.endswith(' '.join(map(str, flag_args))))

	@parameterized.expand([
		('long_flag', '--add-lang', 'pl'),
		('short_flag', '-al', 'de'),
	])
	def test_add_language(self, name, command: str, lang: str):
		self.cli.parse(f't {command} {lang}')
		langs = Configurations.get_saved_languages()
		self.assertIn(f'{lang}', langs)

	@parameterized.expand([
		('long_flag', '--remove-lang', 'pl'),
		('short_flag', '-rl', 'de'),
	])
	def test_remove_language(self, name, command: str, lang: str):
		Configurations.add_langs(lang)
		self.cli.parse(f't {command} {lang}')
		langs = Configurations.get_saved_languages()
		self.assertIn(f'{lang}', langs)
