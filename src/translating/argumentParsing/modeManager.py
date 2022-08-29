import functools
from typing import Callable, Generator, Any

from .configurations import Configurations, Configs
from .constants import ValidationErrors, Messages, SHORT_FLAGS, modes_map, FLAGS, ModeTypes, mode_types_to_modes, \
    modes_to_arity_map
from .layoutAdjusting import layoutAdjusterFactory


class ModesManager:  # TODO: create a mode filter class. Consider creating a subpackage

    @staticmethod
    def show_help() -> None:
        ModesManager._show_syntax()
        ModesManager._show_modes()

    @staticmethod
    def _show_syntax() -> None:
        print('(X) - obligatory if not default')
        print('<X> - obligatory variable given by the user')
        print('[X] - optional - taken from memory/config if not given')
        print('[X]N - optional - the number indicates the order of disappearing')

        print('Single mode     (-s):          trans <word> [from_language]1 [to_language]2')
        print('Multi lang mode (-m):          trans <word> [from_language] (-m) [to_languages...]')
        print('      --||--                   --translates to many languages. If no language after "-m" flag given, the limit-amount of languages are taken'\
                                              'from the memory.')
        print('Multi word mode (-w):          trans [from_language]1 [to_language]2 (-w) <words...>')
        print('      --||--                   --translates many words.')
        print('double multi mode (-m, -w):    trans [from_language] -m <to_languages...> -w <words...>')
        print('      --||--                   trans [from_language] -w <words...> -m <to_languages...>')
        print('      --||--                   --joins functionalities of -m and -w modes')

    @staticmethod
    def _show_modes() -> None:
        space_1 = 18
        space_2 = 24
        for name, mode in {name: SHORT_FLAGS.__dict__[name] for name in SHORT_FLAGS.__dict__ if name[0] != '_'}.items():
            first = f'{modes_map[mode]},'
            second = first + ' ' * (space_1 - len(first)) + mode
            third = second + ' ' * (space_2 - len(second)) + f':{name}'
            print(third)

    def __init__(self):
        self._modes: dict[str, list] = {}
        lang_adjustment_type = Configurations.get_conf(Configs.LANG_SPEC_ADJUSTMENT)
        self._layout_adjuster = layoutAdjusterFactory.get_layout_adjuster(lang_adjustment_type)

    def get_mode_args(self, mode: str) -> list[str | Any]:
        return self._modes[mode][1:] if mode in self._modes else []

    def get_mode_position(self, mode):
        return self._modes[mode][0]

    def add_default_mode(self, mode: str, args=None):
        self._modes[mode] = args or []

    def filter_modes_out_of_args(self, args: list[str]) -> list[str]:
        i = 0
        while 0 <= i < len(args):
            i = self._find_index_of_next_arg(i, args)
            if i == len(args):
                break
            arg = self._get_key_for_arg(args[i])
            del args[i]
            self._add_mode_with_index(arg, i)

            last_mode_argument_index = self._get_last_index_of_mode_argument(i, arg, args)
            self._modes[arg].extend(args[i:last_mode_argument_index])
            del args[i:last_mode_argument_index]
        return args

    def _find_index_of_next_arg(self, i: int, args: list[str]) -> int:
        while len(args) > i and not self._is_mode(args[i]):
            i += 1
        return i

    def _is_mode(self, arg: str) -> bool:
        return arg.startswith('-')

    def _get_key_for_arg(self, arg: str) -> str:
        if self._layout_adjuster:
            arg = self._layout_adjuster.adjust_word(arg)
        if arg in modes_map:
            arg = modes_map[arg]
        return arg

    def _add_mode_with_index(self, arg: str, index: int):
        if arg not in self._modes:
            self._modes[arg] = [index]
        else:
            self._modes[arg].append(index)

    def get_max_arity(self, mode: str) -> int:
        return functools.reduce(lambda m1, m2: m1 if m1 > m2 else m2,
                                (modes_to_arity_map[modes] for modes in modes_to_arity_map if mode in modes)) \
               or 0

    def _get_last_index_of_mode_argument(self, i: int, arg: str, args: list[str]):  # TODO: think of refactor
        arity: int = self.get_max_arity(arg)
        if len(args) < i + arity:
            arity = len(args) - i

        last = i + arity if arity >= 0 else len(args)
        j = self._find_index_of_next_arg(i, args)

        if last > j:
            last = j
        return last

    def validate_modes(self) -> list[str]:
        error_messages = []
        if not self._valid_translational_mode():
            msg = ValidationErrors.MULTI_TRANSLATION_MODES_ON.format()
            error_messages.append(msg)
        return error_messages

    def _valid_translational_mode(self) -> bool:
        num_modes_tuened_on = sum(1 for mode in self._modes if mode in self.get_modes_turned_on_by_type(ModeTypes.TRANSLATIONAL))
        return num_modes_tuened_on < 2 or FLAGS.SINGLE not in self._modes

    def is_mode_explicitly_on(self, mode: str) -> bool:
        return mode in self._modes

    def is_translational_mode_on(self, mode: str):
        return self.is_mode_explicitly_on(mode) or (not self.is_any_translational_mode_on() and Configurations.get_conf(Configs.DEFAULT_TRANSLATIONAL_MODE) == mode)

    def is_multi_lang_mode_on(self) -> bool:
        return self.is_translational_mode_on(FLAGS.MULTI_LANG) and len(list(self.get_modes_turned_on_by_type(ModeTypes.TRANSLATIONAL))) == 1

    def is_multi_word_mode_on(self) -> bool:
        return self.is_translational_mode_on(FLAGS.MULTI_WORD) and len(list(self.get_modes_turned_on_by_type(ModeTypes.TRANSLATIONAL))) == 1

    def is_double_multi_mode_on(self) -> bool:
        return self.is_translational_mode_on(FLAGS.MULTI_WORD) and self.is_translational_mode_on(FLAGS.MULTI_LANG)

    def is_single_mode_on(self) -> bool:
        return self.is_translational_mode_on(FLAGS.SINGLE)

    def is_any_mode_turned_on_by_type(self, type: str) -> bool:
        return any(self.get_modes_turned_on_by_type(type))

    def get_active_translational_modes(self):
        modes = list(self.get_modes_turned_on_by_type(ModeTypes.TRANSLATIONAL))
        if not modes:
            modes = [Configurations.get_conf(Configs.DEFAULT_TRANSLATIONAL_MODE)]
        return modes

    def get_modes_turned_on_by_type(self, type: str) -> Generator[str, None, None]:
        if type not in mode_types_to_modes:
            raise ValueError(Messages.WRONG_MODE_TYPE.format(type))
        is_mode_condition_satisfied = self._get_mode_turn_on_condition_by_type(type)
        return (mode for mode in self._modes if mode in mode_types_to_modes[type] and is_mode_condition_satisfied(mode))

    def _get_mode_turn_on_condition_by_type(self, type: str) -> Callable[[str], bool]:
        if type == ModeTypes.DISPLAYABLE:
            return lambda mode: len(self._modes[mode]) == 1
        if type == ModeTypes.CONFIGURATIONAL:
            return lambda mode: len(self._modes[mode]) > 1
        return lambda mode: True

    def is_any_translational_mode_on(self) -> bool:
        return self.is_any_mode_turned_on_by_type(ModeTypes.TRANSLATIONAL)

    def is_any_displayable_mode_on(self) -> bool:
        return self.is_any_mode_turned_on_by_type(ModeTypes.DISPLAYABLE)

    def is_any_configurational_mode_on(self) -> bool:
        return self.is_any_mode_turned_on_by_type(ModeTypes.CONFIGURATIONAL)
