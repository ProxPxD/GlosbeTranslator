from .configurations import Configurations
from .constants import FullModes, ModeTypes
from .intelligentArgumentParser import IntelligentArgumentParser
from .modeManager import ModesManager


def display_information(argument_parser: IntelligentArgumentParser):
    for to_display in argument_parser.modes.get_modes_turned_on_by_type(ModeTypes.DISPLAYABLE):
        if to_display == FullModes.SETTINGS:
            display_configs(FullModes.DEFAULT_TRANSLATIONAL_MODE, FullModes.LANG_LIMIT, FullModes.SAVED_LANGS)
            continue
        if to_display == FullModes.HELP:
            ModesManager.show_help()
            continue
        display_config(to_display)


def display_configs(*config_names: str):  # TODO: implement help and input modes validation
    for to_display in config_names:
        display_config(to_display)


def display_config(config_name: str):
    conf_to_display = Configurations.get_conf(config_name)
    if isinstance(conf_to_display, list):
        conf_to_display = str(conf_to_display)[1:-1].replace("'", '')
    print(f'{config_name[2:]}: {conf_to_display}')