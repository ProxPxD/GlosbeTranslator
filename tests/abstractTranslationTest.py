import abc
import time
import unittest

from src.translating.argumentParsing.configurations import Configurations, Configs
from src.translating.argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from src.translating.constants import TranslationParts
from src.translating.translator import Translator


class AbstractTranslationTest(unittest.TestCase, abc.ABC):

    argumentParser: IntelligentArgumentParser = None
    translator: Translator = Translator()
    half_sep_length = 40
    currentResult = None

    @classmethod
    def print_sep_with_text(cls, text: str, sep: str = '*') -> None:
        with_sep_lines = sep * cls.half_sep_length + f' {text} ' + sep * cls.half_sep_length
        over_length = len(with_sep_lines) - cls.half_sep_length*2
        to_print = with_sep_lines[over_length//2 : -over_length//2]
        print(to_print)

    @classmethod
    def setUpClass(cls) -> None:
        Configurations.init()
        Configurations.change_conf(Configs.SAVED_LANGS, ['pl', 'en', 'de', 'es', 'uk', 'zh'])
        Configurations.change_conf(Configs.DEFAULT_TRANSLATIONAL_MODE, cls._get_mode())
        cls.print_sep_with_text(f'Starting {cls._get_test_name()} tests!')

    def setUp(self) -> None:
        super().setUp()
        print('- ', self.get_method_name(), end=' ... ')

    def tearDown(self) -> None:
        super().tearDown()
        if self.currentResult is not None:
            errors = self.currentResult.errors
            failures = self.currentResult.failures
            ok = not (errors or failures)
            print('ok' if ok else 'ERROR' if errors else 'FAIL')
        else:
            print()
        time.sleep(0.4)  # wait not to overload the server

    def run(self, result: unittest.result.TestResult | None = ...) -> unittest.result.TestResult | None:
        self.currentResult = result
        unittest.TestCase.run(self, result)

    @abc.abstractmethod
    def _perform_translation(self):
        pass

    @classmethod
    @abc.abstractmethod
    def _get_mode(cls) -> str | None:
        return None

    @classmethod
    @abc.abstractmethod
    def _get_test_name(cls) -> str:
        return 'unnamed'

    def set_input_string(self, input_string: str):
        AbstractTranslationTest.argumentParser = IntelligentArgumentParser(input_string.split(' '))

    def get_constant_part(self, translation: tuple):
        return translation[0]

    def get_nth_translation_batch(self, index: int, translation: tuple[str, list]):
        return translation[1][index]

    def get_nth_translated_word(self, index: int, translation: tuple[str, list]):
        return translation[1][index][TranslationParts.TRANSLATION]

    def get_word_from_batch(self, batch):
        return batch[TranslationParts.TRANSLATION]

    def get_gender_from_batch(self, batch):
        return batch[TranslationParts.GENDER]

    def get_part_of_speech_from_batch(self, batch):
        return batch[TranslationParts.PART_OF_SPEECH]

    def translate(self) -> list:
        AbstractTranslationTest.argumentParser.parse()
        translation = self._perform_translation()
        return list(translation)

    def get_method_name(self) -> str:
        return self.id().split('.')[-1]
