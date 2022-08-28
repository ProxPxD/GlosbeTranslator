from .configurations import Configurations
from .constants import FLAGS, ModeTypes
from .intelligentArgumentParser import IntelligentArgumentParser
from .modeManager import ModesManager


def display_information(argument_parser: IntelligentArgumentParser):
    for to_display in argument_parser.modes.get_modes_turned_on_by_type(ModeTypes.DISPLAYABLE):
        if to_display == FLAGS.SETTINGS:
            display_configs(FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.LANG_LIMIT, FLAGS.SAVED_LANGS)
            continue
        if to_display == FLAGS.HELP:
            ModesManager.show_help()
            continue
        display_config(to_display)


def display_configs(*config_names: str):  # TODO: implement help and input modes validation
    for to_display in config_names:
        display_config(to_display)


def display_config(config_name: str):
    conf_to_display = Configurations.get_conf(config_name)
    conf_to_display = format_config(conf_to_display)
    print(f'{config_name[2:]}: {conf_to_display}')

    possible_values = Configurations.get_possible_values_for(config_name)
    if possible_values:
        display_possible_values(possible_values)


def format_config(config: list | str):
    if isinstance(config, list):
        return list_to_comma_string(config)
    return str(config)


def list_to_comma_string(list_to_transform: list | str):
    return str(list_to_transform)[1:-1].replace("'", '')


def display_possible_values(possible_values: list | str):
    possible_values = format_config(possible_values)
    print(f'Possible values: {possible_values}')
