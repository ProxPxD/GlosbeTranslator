from dataclasses import dataclass


@dataclass(frozen=True)
class Modes:
    MULTI_LANG: str = '-m'
    MULTI_WORD: str = '-w'
    SINGLE: str = '-s'


@dataclass(frozen=True)
class FullModes:
    MULTI_LANG_FULL: str = '--multi'
    MULTI_WORD_FULL: str = '--word'
    SINGLE_FULL: str = '--single'


_modes_map = {
    FullModes.MULTI_LANG_FULL: Modes.MULTI_LANG,
    FullModes.MULTI_WORD_FULL: Modes.MULTI_WORD,
    FullModes.SINGLE_FULL: Modes.SINGLE
}

_modes_to_arity_map = {
    (Modes.MULTI_LANG, Modes.MULTI_WORD): -1,
    (Modes.SINGLE): 0,
    (): 1
}


class ModesManager:

    def __init__(self):
        self._modes: dict[str, list] = {}

    def get_arity(self, mode: str) -> int:
        return next((_modes_to_arity_map[modes] for modes in _modes_to_arity_map if mode in modes), 0)

    def filter_modes_out_of_args(self, args: list):  # TODO: look for a clean-code refactor
        i = 0
        while 0 <= i < len(args):
            arg = args[i]
            if not self._is_mode(arg):
                i += 1
                continue

            if arg not in self._modes:
                self._modes[arg] = []
            del args[i]
            arity: int = self.get_arity(arg)
            last_mode_argument_index: int = i + arity
            self._modes[arg].extend(args[i:last_mode_argument_index])
            del args[i:last_mode_argument_index]
            i = last_mode_argument_index
        return args

    def _is_mode(self, arg: str):
        return arg.startswith('-')

    def validate_modes(self):  # TODO: check how to do a good validation
        is_valid = True
        is_valid = is_valid and self._valid_parsing_mode()
        return is_valid

    def _valid_parsing_mode(self):
        return sum(1 for mode in self._modes if mode in self._get_parsing_modes()) <= 1

    def _get_parsing_modes(self):
        return [Modes.SINGLE, Modes.MULTI_WORD, Modes.MULTI_LANG]

    def is_mode_on(self, mode: str):
        return mode in self._modes

    def is_multi_lang_mode_on(self):
        return self.is_mode_on(Modes.MULTI_LANG)

    def is_multi_word_mode_on(self):
        return self.is_mode_on(Modes.MULTI_WORD)

    def is_single_mode_on(self):
        return not (self.is_multi_lang_mode_on() or self.is_multi_word_mode_on()) or self.is_mode_on(Modes.SINGLE)