from time import sleep

from parameterized import parameterized

from src.glosbe.configurations import Configurations
from src.glosbe.translating.translator import TranslationTypes
from src.glosbe.translatingPrinting.formatting import TranslationFormatter
from src.glosbe.translatingPrinting.translationPrinter import TranslationPrinter
from src.glosbe.translatorCli import SILENT_LONG_FLAG, SINGLE_LONG_FLAG, DOUBLE_MODE_STYLE_LONG_FLAG
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

	@parameterized.expand([
		('by_lang', TranslationTypes.LANG),
		('by_word', TranslationTypes.WORD),
		('by_nothing_with_single', TranslationTypes.SINGLE),
		('by_nothing_with_double', TranslationTypes.DOUBLE),
	])
	def test_double_mode_formatting(self, name: str, style: str, e_group: list[str], e_prefixes: list[str]):
		if style:
			Configurations.set_conf(DOUBLE_MODE_STYLE_LONG_FLAG, style)
		langs = 'zh ar'.split(' ')
		words = 'Welt Schmerz'.split()
		result = self.cli.parse(f't de -w {" ".join(words)} -m {" ".join(langs)}')

		main_division = style
		prefix_style = self.cli._get_prefix_style_for_main_division(main_division)
		formatted = TranslationFormatter.format_many(result.result)
		string = TranslationFormatter.format_many_into_string(formatted, prefix_style=prefix_style, main_division=main_division)
		lines = string.split('\n')
		group_iter = iter(e_group)
		prefix_iter = iter(e_prefixes)

		for i, line in enumerate(lines):
			if e_group and i % 3 == 0:
				self.assertIn(next(group_iter), line)
				prefix_iter = iter(e_prefixes)
			elif e_group:
				self.assertTrue(line.startswith(f'{next(prefix_iter)}: '))
			else:
				self.fail(NotImplementedError.__name__)


'''
---- zh ----------------------------------------------------------------
what: 什么 [adverb; particle; pronoun] (pronoun); 什麼 [adverb; particle; pronoun] (pronoun); 啥 (pronoun); What's
is: 是 (verb); ‘be’; 做; 收入补助; 收入补贴; 综合调查the: 愈......愈...... (adv.); 越......越...... (adv.); 这 (noun)
sense: 感覺 [verb] (noun); 意义 (noun); 感觉 [verb] (noun)
of: 的 (adposition); 之 (adposition); 关于 (adposition)
life: 生命 (noun); 生活 (noun); 存在 (noun); 生命 (noun)
---- de ----------------------------------------------------------------
what: was [pronoun] (adv.); welcher [pronoun] (adj.); wie (pronoun)
is: ist (verb); alles paletti; es gibt (verb); I (noun); In (noun); IS (noun)
the: der [article] (Article); die [article] (Article); das [article] (Article); transkription
sense: Sinn [masc] (noun); fühlen (verb); empfinden (verb); Sensebezirk
of: von (adposition); aus (adposition); vor (adposition)
life: Leben [neut] (noun); Lebensdauer [fem] (noun); lebenslänglich (noun); Leben (noun); Spiel des Lebens; Das Leben; Lebenslänglich
---- ru ----------------------------------------------------------------
what: что [adverb] (pronoun); какой [determiner] (adv.); который [determiner] (pronoun)
is: есть (verb); есть ’to be; идти (verb); информационная система; комплексное обследование; поддержка малоимущих
the: тем (adv.); тот (pronoun); такой (determiner); транскрипция (noun)
sense: чувство [neut] (noun); смысл [masc] (noun); чувствовать [impf] (verb)
of: из (noun); о (noun); в (noun)
life: жизнь [fem] (noun); житие [fem] (noun); существование [neut] (noun); Жизнь
---- pl ----------------------------------------------------------------
what: co [pronoun] (adv.); jaki [pronoun] (determiner); który [pronoun] (determiner)
is: jest (verb); być (verb); PI
the: ten [masc] (pronoun); to [neut] (pronoun); ta [fem] (pronoun); transkrypcja (noun)
sense: zmysł [masc] (noun); sens [masc] (noun); odczuwać (verb)
of: z (adposition); u (adposition); o (adv.)
life: życie [neut] (noun); dożywocie [neut] (noun); kara dożywotniego pozbawienia wolności [fem] (noun); Życie
'''