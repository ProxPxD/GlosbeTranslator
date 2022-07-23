from abc import ABC, abstractmethod

from argumentParsing import configurations


class AbstractArgumentParser(ABC):

    def __int__(self, args: list[str, ...]):
        self._args: list[str, ...] = args
        self._modes = []
        self._words = []
        self._from_lang = None
        self._to_langs = []

    @abstractmethod
    def parse(self):
        pass

    def _has_arg(self, i: int):
        return i < len(self._args)

    def _get_arg_or_config_if_non(self, i: int, config_name: str):
        return self._args[i] if self._has_arg(i) else configurations.get_conf(config_name)

    def _collect_modes(self):
        self._modes = [arg for arg in self._args if self._is_mode(arg)]
        self._args = [arg for arg in self._args if not self._is_mode(arg)]
        return self._modes

    def _is_mode(self, arg: str):
        return arg.startswith('-')