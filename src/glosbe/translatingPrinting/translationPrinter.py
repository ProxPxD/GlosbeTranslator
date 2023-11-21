import time
from time import sleep
from typing import Iterable, Any

from .formatting import TranslationFormatter
from ..translating.scrapping import TranslationResult


class TranslationPrinter:
    out_func = lambda to_print: print(to_print, end='')
    _is_turned_on = True
    break_time = 0.2

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
        if end:
            cls.out_func(f'{to_print}{end}')
        else:
            cls.out_func(to_print)

    @classmethod
    def print_with_formatting(cls, translations: Iterable[TranslationResult], **kwargs) -> None:
        formatted = TranslationFormatter.format_many(translations, **kwargs)
        cls.print(formatted, **kwargs)

    @classmethod
    def print(cls, translations: Iterable[TranslationResult], **kwargs) -> None:
        if not cls._is_turned_on:
            return
        printable = TranslationFormatter.format_many_into_printable_iterable(translations, **kwargs)
        curr_time = time.time()
        for to_print in printable:
            cls.out(to_print, end='')
            iter_time = time.time()
            elapsed_time = iter_time - curr_time
            if cls.break_time - elapsed_time > 0:
                sleep(cls.break_time - elapsed_time)
            curr_time = time.time()