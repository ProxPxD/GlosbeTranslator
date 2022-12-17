from parameterized import parameterized

from tests.abstractCliTest import AbstractCliTest


class FunctionalFlagsTest(AbstractCliTest):
	@classmethod
	def _get_test_name(cls) -> str:
		return 'Functional Flags'

	@parameterized.expand([
		('short_reverse_flag', 't żal de pl -r', ['żal'], ['pl'], ['de']),
	])
	def test_parsed_arguments(self, name: str, input_line: str, e_words: list[str], e_from_langs: list[str], e_to_langs: list[str]):
		words, from_lang, to_langs = self.cli.root.get_collections('words', 'from_langs', 'to_langs')
		self.cli.parse(input_line)

		self.assertCountEqual(e_words, words.get_as_list())
		self.assertCountEqual(e_from_langs, from_lang.get_as_list())
		self.assertCountEqual(e_to_langs, to_langs.get_as_list())