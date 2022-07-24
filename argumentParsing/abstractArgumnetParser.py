from abc import ABC, abstractmethod


class AbstractArgumentParser(ABC):

    def __init__(self, args: list[str, ...]):
        self._args: list[str, ...] = args[1:]
        self._modes = []
        self._words = []
        self._from_lang = None
        self._to_langs = []

    @property
    def from_lang(self):
        return self._from_lang

    @property
    def to_langs(self):
        return self._to_langs

    @property
    def words(self):
        return self._words

    @abstractmethod
    def parse(self):
        pass

    def _has_arg(self, i: int):
        return i < len(self._args)

    def _get_arg_else_none(self, i: int):
        return self._args[i] if self._has_arg(i) else None

    def _is_mode(self, arg: str):
        return arg.startswith('-')