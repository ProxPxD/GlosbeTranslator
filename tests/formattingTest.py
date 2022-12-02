from typing import Any

from parameterized import parameterized

from src.translating.translatingPrinting.formatting import GenderFormatter, PartOfSpeechFormatter, AbstractFormatter
from tests.abstractTest import AbstractTest


class FormattingTest(AbstractTest):

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Formatting'

	@parameterized.expand([  # TODO: Extend later
		('feminine', 'fem', GenderFormatter), ('adjective', 'adj.', PartOfSpeechFormatter), ],
		name_func=lambda method, param_num, param: f'{method.__name__}_{param_num}_format_{param.args[0]}_with_{param.args[2].__name__}')
	def test_formatter(self, arg: Any, expected: Any, formatter: AbstractFormatter):
		self.assertEqual(expected, formatter.format(arg))
