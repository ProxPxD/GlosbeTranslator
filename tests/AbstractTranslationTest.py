import unittest

from src.translating.argumentParsing.configurations import Configurations
from src.translating.argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from src.translating.translator import Translator
import abc


class AbstractTranslationTest(unittest.TestCase, abc.ABC):

    argumentParser: IntelligentArgumentParser = None
    translator: Translator = Translator()

    @classmethod
    def setUpClass(self) -> None:
        Configurations.init()

    def set_input_string(self, input_string: str):
        AbstractTranslationTest.argumentParser = IntelligentArgumentParser(input_string.split(' '))

    def translate(self):
        AbstractTranslationTest.argumentParser.parse()
        translation = self._perform_translation()
        return list(translation)

    @abc.abstractmethod
    def _perform_translation(self):
        pass
