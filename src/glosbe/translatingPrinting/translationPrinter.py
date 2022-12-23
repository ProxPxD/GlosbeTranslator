from typing import Iterable, Any

from .formatting import TranslationFormatter
from ..translating.translator import TranslationResult


class TranslationPrinter:
    out_func = print
    _is_turned_on = True

    @classmethod
    def turn_off(cls) -> None:
        cls.turn(False)

    @classmethod
    def turn_on(cls) -> None:
        cls.turn(True)

    @classmethod
    def turn(cls, state: bool) -> None:
        cls._is_turned_on = state

    @classmethod
    def out(cls, to_print: Any, end=None) -> None:
        if not cls._is_turned_on:
            return
        if end is not None:
            cls.out_func(to_print, end=end)
        else:
            cls.out_func(to_print)

    @classmethod
    def print_with_formatting(cls, translations: Iterable[TranslationResult], *, prefix_style=None, main_division=None) -> None:
        formatted = TranslationFormatter.format_many(translations)
        cls.print(formatted, prefix_style=prefix_style, main_division=main_division)

    @classmethod
    def print(cls, translations: Iterable[TranslationResult], prefix_style=None, main_division=None) -> None:
        if not cls._is_turned_on:
            return
        printable = TranslationFormatter.format_many_into_printable_iterable(translations, prefix_style=prefix_style, main_division=main_division)
        for to_print in printable:
            cls.out(to_print, end='')