from typing import Iterable

from .formatting import TranslationFormatter
from ..translator import TranslationResult


class TranslationPrinter:
    out = print

    @classmethod
    def print_with_formatting(cls, translations: Iterable[TranslationResult], *, prefix_style=None, main_division=None) -> None:
        formatted = TranslationFormatter.format_many(translations)
        cls.print(formatted, prefix_style=prefix_style, main_division=main_division)

    @classmethod
    def print(cls, translations: Iterable[TranslationResult], prefix_style=None, main_division=None) -> None:
        printable = TranslationFormatter.format_many_into_printable_iterable(translations, prefix_style=prefix_style, main_division=main_division, level=1)
        for to_print in printable:
            cls.out(to_print, end='')
