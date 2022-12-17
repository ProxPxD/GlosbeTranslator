import abc

from src.translating.argumentParsing.translatorCli import TranslatorCli
from tests.abstractTest import AbstractTest


class AbstractCliTest(AbstractTest, abc.ABC):
	cli = TranslatorCli()

	@classmethod
	def setUpClass(cls) -> None:
		super().setUpClass()
		cls.cli.turn_off_translating()

	@classmethod
	def tearDownClass(cls) -> None:
		cls.cli.turn_on_translating()

	def get_file_name(self) -> str:
		return self._get_test_name()

