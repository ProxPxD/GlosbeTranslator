import functools


class ModeFilter:  # TODO: finish creating the class and move common logic to a separate class. Consider creating a subpackage

    def __init__(self):
        self._args: list[str] = []
        self._modes = {}

    def set_args(self, args: list[str]) -> None:
        self._args = args

    def filter_modes_out_of_args(self, args: list[str]) -> list[str]:
        self.set_args(args)
        self._modes = {}
        i = 0
        while 0 <= i < len(self._args):
            i = self._find_index_of_next_arg(i, args)
            arg = self._get_key_for_arg(args[i])
            del args[i]
            self._initialize_modes_dictionary_if_needed(arg)

            last_mode_argument_index = self._get_last_index_of_mode_argument(i, arg, args)
            self._modes[arg].extend(args[i:last_mode_argument_index])
            del args[i:last_mode_argument_index]
            i = last_mode_argument_index
        return args

    def _find_index_of_next_arg(self, i: int, args: list[str]) -> int:
        while not self._is_mode(args[i]):
            i += 1
        return i

    def _is_mode(self, arg: str):
        return arg.startswith('-')

    def _get_key_for_arg(self, arg: str) -> str:
        if arg in _modes_map:
            arg = _modes_map[arg]
        return arg

    def _initialize_modes_dictionary_if_needed(self, arg: str):
        if arg not in self._modes:
            self._modes[arg] = []

    def get_max_arity(self, mode: str) -> int:
        return functools.reduce(lambda m1, m2: m1 if m1 > m2 else m2,
                                (_modes_to_arity_map[modes] for modes in _modes_to_arity_map if mode in modes))

    def _get_last_index_of_mode_argument(self, i: int, arg: str, args: list[str]):
        arity: int = self.get_max_arity(arg)
        if len(args) < i + arity:
            arity = len(args) - i
        return i + arity
