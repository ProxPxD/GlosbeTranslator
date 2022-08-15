import unittest

from src.translating.argumentParsing.configurations import Configurations, Configs
from src.translating.argumentParsing.intelligentArgumentParser import IntelligentArgumentParser
from src.translating.constants import TranslationParts
from src.translating.translator import Translator
import abc


class AbstractTranslationTest(unittest.TestCase, abc.ABC):

    argumentParser: IntelligentArgumentParser = None
    translator: Translator = Translator()
    class_sep_size = 20

    @classmethod
    def setUpClass(cls) -> None:
        Configurations.init()
        Configurations.change_conf(Configs.SAVED_LANGS, ['pl', 'en', 'de', 'es', 'uk', 'zh'])
        Configurations.change_conf(Configs.DEFAULT_TRANSLATIONAL_MODE, cls._get_mode())
        print('*' * cls.class_sep_size + f' Starting {cls._get_mode()} mode tests! ' + '*' * cls.class_sep_size)

    @abc.abstractmethod
    def _perform_translation(self):
        pass

    @classmethod
    @abc.abstractmethod
    def _get_mode(cls) -> str:
        return None

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

    def translate(self):
        AbstractTranslationTest.argumentParser.parse()
        translation = self._perform_translation()
        return list(translation)
