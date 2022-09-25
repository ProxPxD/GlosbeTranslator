import abc
import time

from src.translating.configs.configurations import Configurations, Configs
from tests.abstractTest import AbstractTest


class AbstractTranslationTest(AbstractTest, abc.ABC):

    def tearDown(self) -> None:
        super(AbstractTranslationTest, self).tearDown()
        time.sleep(0.4)  # wait not to overload the server

    @classmethod
    def setUpClass(cls) -> None:
        super(AbstractTranslationTest, cls).setUpClass()
        Configurations.change_conf(Configs.DEFAULT_TRANSLATIONAL_MODE, cls._get_mode())

    @classmethod
    @abc.abstractmethod
    def _get_mode(cls) -> str | None:
        return None