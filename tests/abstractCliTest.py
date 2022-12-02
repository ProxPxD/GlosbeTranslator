import abc

from src.translating.argumentParsing.translatorCli import TranslatorCli
from tests.abstractTest import AbstractTest


class AbstractCliTest(AbstractTest, abc.ABC):
    cli = TranslatorCli()
