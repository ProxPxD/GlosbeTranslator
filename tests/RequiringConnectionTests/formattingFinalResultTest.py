from time import sleep

from parameterized import parameterized

from src.glosbe.configurations import Configurations
from src.glosbe.translating.translator import TranslationTypes
from src.glosbe.translatingPrinting.formatting import TranslationFormatter
from src.glosbe.translatingPrinting.translationPrinter import TranslationPrinter
from src.glosbe.translatorCli import SILENT_LONG_FLAG, SINGLE_LONG_FLAG
from tests.abstractCliTest import AbstractCliTest


class FormattingFinalResultTest(AbstractCliTest):

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Formatting Final Result'

	@classmethod
	def setUpClass(cls) -> None:
		super().setUpClass()
		cls.cli.turn_on_translating()

	def setUp(self) -> None:
		super().setUp()
		Configurations.init(self.get_file_name(), default=self.get_default_configs())
		Configurations.add_langs('es', 'pl', 'de', 'ar')
		Configurations.change_conf('-l', 3)
		TranslationPrinter.turn(False)
		sleep(1)

	def tearDown(self) -> None:
		super().tearDown()
		# Configurations.remove_current_configuration()

	@parameterized.expand([
		('all_args', 't piec pl es', ['horno [masc] (noun);', ' hornear (verb);'], []),
		('no_from_lang', 't piec de', ['backen (verb);', 'Ofen [masc] (noun);'], ['pl', 'de']),
		('only_word', 't piec', ['horno [masc] (noun);', ' hornear (verb); '], ['pl', 'es']),
	])
	def test_single_mode_formatting(self, name: str, input_line: str, expected_in_formatted: list[str], last_langs: list[str, str]):
		if last_langs:
			Configurations.change_last_used_languages(*last_langs)

		input_line += f' {SILENT_LONG_FLAG} {SINGLE_LONG_FLAG}'

		result = self.cli.parse(input_line)
		formatted = TranslationFormatter.format_many(result.result)
		string = TranslationFormatter.format_many_into_string(formatted)
		for expected in expected_in_formatted:
			self.assertIn(expected, string)
		self.assertTrue(string.endswith('\n'))
		self.assertFalse(string.startswith(('pl', 'de', 'es', '\n', ' ', 'piec')))

	@parameterized.expand([
		('multi', 't piec pl -m ar es', ['ar', 'es'], []),
		('multi_with_pre_flag', 't piec pl zh -m ar es', ['ar', 'es', 'zh'], []),
		('multi_no_from_lang', 't piec -m ar es', ['ar', 'es'], ['pl']),
		('multi_to_langs_from_config', 't piec pl -m', ['es', 'de', 'ar'], ['es', 'de', 'ar']),
		('word', 't de pl -w Zeitgeist Weltschmerz Fernweh Zugzwang', ['Zeitgeist', 'Weltschmerz', 'Fernweh'], []),
		('word', 't de pl Zugzwang Schadenfreude -w', ['Zugzwang', 'Schadenfreude'], []),
		('word', 't pl -w Zugzwang Schadenfreude', ['Zugzwang', 'Schadenfreude'], ['de', 'ar']),
		('word', 't -w Zugzwang Schadenfreude', ['Zugzwang', 'Schadenfreude'], ['de', 'ar']),
	])
	def test_word_and_multi_mode_formatting(self, name: str, input_line: str, prefixes: list[str], last_langs: list[str, str]):
		if last_langs:
			Configurations.change_last_used_languages(*last_langs)

		prefix_style = TranslationTypes.WORD if '-w' in input_line else TranslationTypes.LANG

		input_line += f' {SILENT_LONG_FLAG}'
		result = self.cli.parse(input_line)
		formatted = TranslationFormatter.format_many(result.result)
		string = TranslationFormatter.format_many_into_string(formatted, prefix_style=prefix_style)
		lines = string.split('\n')
		for prefix, line in zip(prefixes, lines):
			self.assertTrue(line.startswith(f'{prefix}: '), msg=f'prefix {prefix} not found in line {line}!')
		# self.assertTrue(lines[-1] == '')

	def test_double_mode_formatting(self):
		langs = 'zh de ru pl'.split(' ')
		words = 'what is the sense of life'.split()
		self.cli.parse(f't en -w {" ".join(words)} -m {" ".join(langs)}')

		self.fail(NotImplementedError.__name__)