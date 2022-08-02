import functools
from dataclasses import dataclass


@dataclass(frozen=True)
class Modes:
    MULTI_LANG: str = '-m'
    MULTI_WORD: str = '-w'
    SINGLE: str = '-s'
    LANG_LIMIT: str = '-l'
    SAVED_LANGS: str = '-ll'
    LAST: str = '-1'
    DEFAULT_TRANSLATIONAL_MODE: str = '-dm'


@dataclass(frozen=True)
class FullModes:
    MULTI_LANG: str = '--multi'
    MULTI_WORD: str = '--word'
    SINGLE: str = '--single'
    LANG_LIMIT: str = '--limit'
    SAVED_LANGS: str = '--langs'
    LAST: str = '--last'
    DEFAULT_TRANSLATIONAL_MODE: str = '--default_mode'


_modes_map = {
    Modes.MULTI_LANG: FullModes.MULTI_LANG,
    Modes.MULTI_WORD: FullModes.MULTI_WORD,
    Modes.SINGLE: FullModes.SINGLE,
    Modes.LANG_LIMIT: FullModes.LANG_LIMIT,
    Modes.SAVED_LANGS: FullModes.SAVED_LANGS,
    Modes.LAST: FullModes.LAST,
    Modes.DEFAULT_TRANSLATIONAL_MODE: FullModes.DEFAULT_TRANSLATIONAL_MODE
}

_modes_to_arity_map = {
    (FullModes.MULTI_LANG, FullModes.MULTI_WORD): -1,
    (FullModes.SINGLE, FullModes.SAVED_LANGS, FullModes.LANG_LIMIT, FullModes.LAST): 0,
    (FullModes.LANG_LIMIT, FullModes.LAST): 1
}

_translational_modes = {FullModes.SINGLE, FullModes.MULTI_WORD, FullModes.MULTI_LANG}

_display_modes = {FullModes.LANG_LIMIT, FullModes.SAVED_LANGS, FullModes.LAST}

_configurational_modes = {FullModes.LANG_LIMIT}


class ModesManager:

    def __init__(self):
        self._modes: dict[str, list] = {}

    @property
    def configurational(self):
        return [mode for mode in self._modes if mode in _configurational_modes]

    def get_max_arity(self, mode: str) -> int:
        return functools.reduce(lambda m1, m2: m1 if m1 > m2 else m2,
                                (_modes_to_arity_map[modes] for modes in _modes_to_arity_map if mode in modes))

    def filter_modes_out_of_args(self, args: list):  # TODO: look for a clean-code refactor
        i = 0
        while 0 <= i < len(args):
            arg = args[i]
            if not self._is_mode(arg):
                i += 1
                continue

            if arg not in self._modes:
                if arg in _modes_map:
                    arg = _modes_map[arg]
                self._modes[arg] = []
            del args[i]

            arity: int = self.get_max_arity(arg)
            while len(args) < i + arity:
                arity -= 1
            last_mode_argument_index: int = i + arity

            self._modes[arg].extend(args[i:last_mode_argument_index])
            del args[i:last_mode_argument_index]
            i = last_mode_argument_index
        return args

    def _is_mode(self, arg: str):
        return arg.startswith('-')

    def validate_modes(self):  # TODO: check how to do a good validation
        is_valid = True
        is_valid = is_valid and self._valid_translational_mode()
        return is_valid

    def _valid_translational_mode(self):
        return sum(1 for mode in self._modes if mode in _translational_modes) <= 1

    def is_mode_on(self, mode: str):
        return mode in self._modes

    def is_multi_lang_mode_on(self):
        return self.is_mode_on(FullModes.MULTI_LANG)

    def is_multi_word_mode_on(self):
        return self.is_mode_on(FullModes.MULTI_WORD)

    def is_single_mode_on(self):
        return not (self.is_multi_lang_mode_on() or self.is_multi_word_mode_on()) or self.is_mode_on(FullModes.SINGLE)

    def is_any_display_mode_on(self):
        return any(self.get_display_modes_turned_on())

    def get_display_modes_turned_on(self):
        return (mode for mode in self._modes if self._is_display_mode_on(mode))

    def _is_display_mode_on(self, mode: str):
        return mode in _display_modes and len(self._modes[mode]) == 0

    def is_any_configurational_mode_on(self):
        return any(self.get_display_modes_turned_on())

    def get_configurational_modes_turned_on(self):
        return (mode for mode in self._modes if self._is_configurational_mode_on(mode))

    def _is_configurational_mode_on(self, mode: str):
        return len(self._modes[mode]) > 0 and mode in _configurational_modes