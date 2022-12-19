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

	def test_take_nth_lang(self):
		Configurations.change_conf('--langs', [])
		try:
			Configurations.get_nth_saved_language(0)
			Configurations.get_nth_saved_language(1)
		except Exception:
			self.fail()
