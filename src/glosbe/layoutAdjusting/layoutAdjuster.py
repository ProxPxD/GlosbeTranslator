from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Type, Iterable

import yaml


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
            try:
                adjustings = yaml.safe_load(adj)
                layout = adjustings[self._get_layout()]
                dictionary = layout[self._lang]
                return dictionary
            except LookupError:
                return dict()

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
class LayoutAdjustmentsMethods:
    NONE: str = 'none'
    NATIVE: str = 'native'
    KEYBOARD: str = 'keyboard'

    @classmethod
    def get_adjusting_methods(cls) -> Iterable[str]:
        return list(value for value in cls.__annotations__.keys() if cls.__dict__[value] != cls.NONE)

    @classmethod
    def get_adjuster(cls, method: str) -> Type[AbstractLayoutAdjuster]:
        match method:
            case LayoutAdjustmentsMethods.KEYBOARD:
                return KeyboardLayoutAdjuster
            case LayoutAdjustmentsMethods.NATIVE:
                return NativeLayoutAdjuster
            case _:
                return NoneLayoutAdjuster


class LayoutAdjusterFactory:

    @classmethod
    def get_layout_adjuster(cls, method: str = None, lang: str = None) -> AbstractLayoutAdjuster:
        return LayoutAdjustmentsMethods.get_adjuster(method)(lang)