from parameterized import parameterized

from src.glosbe.configurations import Configurations
from tests.abstractCliTest import AbstractCliTest


class ConfigurationTest(AbstractCliTest):

	@classmethod
	def _get_test_name(cls) -> str:
		return 'Configuration'

	def setUp(self) -> None:
		super().setUp()
		Configurations.init(self.get_file_name(), default=self.get_default_configs())

	def tearDown(self) -> None:
		super().tearDown()
		Configurations.remove_current_configuration()

	def test_take_nth_lang_from_no_langs(self):
		Configurations.change_conf('--langs', [])
		try:
			Configurations.get_nth_saved_language(0)
			Configurations.get_nth_saved_language(1)
		except Exception:
			self.fail()

	@parameterized.expand([
		('first', 'pl', 0),
		('second', 'zh', 1),
		('third', 'es', 2),
		('forth', 'de', 3),
		('out_of_range', None, 4),
	])
	def test_take_nth_lang(self, name: str, expected: str, n: int):
		Configurations.change_conf('--langs', ['pl', 'zh', 'es', 'de'])
		actual = Configurations.get_nth_saved_language(n)
		self.assertEqual(expected, actual)
