from unittest import skipIf

from parameterized import parameterized

from tests.abstractCliTest import AbstractCliTest


class HelpTest(AbstractCliTest):

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Help'

	@parameterized.expand([
		('no_args_in_single', 't -s'),
		('no_args_in_multi', 't -m'),
		('no_args_in_word', 't -w'),
		('no_args_in_double', 't -w -m'),
		('implicit_help', 't -h'),
	])
	@skipIf(lambda: HelpTest.cli.root.help == '', 'no help implemented')
	def test_help_printing(self, name: str, input_line: str):
		self.cli.parse_without_actions(input_line)
		self.fail(NotImplementedError.__name__)
