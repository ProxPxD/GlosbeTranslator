from . import modeManager
from .configurations import Configurations, Configs
from .constants import Messages
from .intelligentArgumentParser import IntelligentArgumentParser
from .modeManager import FullModes, ModeTypes


def set_configs(argument_parser: IntelligentArgumentParser):
    for config_name in argument_parser.modes.get_modes_turned_on_by_type(ModeTypes.CONFIGURATIONAL):
        arguments = argument_parser.modes.get_config_args(config_name)
        set_config(config_name, arguments)


def set_config(config_name: str, arguments: list[str]):
    if config_name == FullModes.ADD_LANG:
        _add_langs(arguments)
    elif config_name == FullModes.REMOVE_LANG:
        _remove_langs(arguments)
    elif config_name == Configs.DEFAULT_TRANSLATIONAL_MODE:
        mode: str = arguments[0]
        if mode in modeManager.modes_map:
            mode = modeManager.modes_map[mode]
        Configurations.change_conf(config_name, mode)
    else:
        Configurations.change_conf(config_name, arguments[0])


def _add_langs(arguments: list[str]):
    langs = Configurations.get_saved_languages()
    for lang in arguments:
        if lang in langs:
            print(Messages.ADD_EXISTENT_LANG.format(lang))
        else:
            langs.append(lang)


def _remove_langs(arguments: list[str]):
    langs = Configurations.get_saved_languages()
    for lang in arguments:
        if lang not in langs:
            print(Messages.REMOVE_NONEXISTENT_LANG.format(lang))
        else:
            langs.remove(lang)