from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Type

import yaml

from src.glosbe.cli.configs.configurations import Configurations, Configs


class AbstractLayoutAdjuster(ABC):

    def __init__(self, adjustment_lang: str = None):
        self._lang = None
        self._dictionary = {}
        self.set_adjustment_lang(adjustment_lang)

    def set_adjustment_lang(self, adjustment_lang):
        if adjustment_lang:
            self._lang = adjustment_lang
            self._dictionary = self._get_dictionary()

    def adjust(self, word: str) -> str:
        return self._dictionary[word] if word in self._dictionary else word

    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        with open("adjusting.yaml", 'r') as adj:
            adjustings = yaml.safe_load(adj)
            layout = adjustings[self._get_layout()]
            dictionary = layout[self._lang] if self._lang in layout else {}
            return dictionary

    @abstractmethod
    def _get_layout(self) -> str:
        raise NotImplementedError


class KeyboardLayoutAdjuster(AbstractLayoutAdjuster):
    def _get_layout(self) -> str:
        return 'keyboard'


class NativeLayoutAdjuster(AbstractLayoutAdjuster):
    def _get_layout(self) -> str:
        return 'native'


class NoneLayoutAdjuster(AbstractLayoutAdjuster):
    def _get_layout(self) -> str:
        return 'none'


@dataclass(frozen=True)
class LayoutAdjustmentsModes:
    NONE: str = 'none'
    NATIVE: str = 'native'
    KEYBOARD: str = 'keyboard'

    @classmethod
    def get_adjuster(cls, mode: str) -> Type[AbstractLayoutAdjuster]:
        match mode:
            case LayoutAdjustmentsModes.KEYBOARD:
                return KeyboardLayoutAdjuster
            case LayoutAdjustmentsModes.NATIVE:
                return NativeLayoutAdjuster
            case _:
                return NoneLayoutAdjuster


class LayoutAdjusterFactory:

    @classmethod
    def get_layout_adjuster(cls, mode: str = None, lang: str = None) -> AbstractLayoutAdjuster:
        mode = mode or Configurations.get_conf(Configs.LANG_SPEC_ADJUSTMENT)
        lang = lang or Configurations.get_conf(Configs.ADJUSTMENT_LANG)
        return LayoutAdjustmentsModes.get_adjuster(mode)(lang)