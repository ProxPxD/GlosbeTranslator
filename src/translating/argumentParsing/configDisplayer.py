from .configurations import Configurations
from .constants import FLAGS, ModeTypes
from .intelligentArgumentParser import IntelligentArgumentParser
from .modeManager import ModesManager


def display_information(argument_parser: IntelligentArgumentParser):
    for to_display in argument_parser.modes.get_modes_turned_on_by_type(ModeTypes.DISPLAYABLE):
        if to_display == FLAGS.SETTINGS:
            display_configs(FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.LANG_LIMIT,
                            FLAGS.SAVED_LANGS, FLAGS.ADJUSTMENT_LANG, FLAGS.LAYOUT_ADJUSTMENT_MODE)
            continue
        if to_display == FLAGS.HELP:
            ModesManager.show_help()
            continue
        display_config(to_display, show_possible=True)


def display_configs(*config_names: str, show_possible=False):  # TODO: implement help and input modes validation
    for to_display in config_names:
        display_config(to_display, show_possible)


def display_config(config_name: str, show_possible=False):
    conf_to_display = Configurations.get_conf(config_name)
    conf_to_display = format_config(conf_to_display)
    print(f'{config_name[2:]}: {conf_to_display}')

    if show_possible:
        display_possible_values(config_name)


def format_config(config: list | str):
    if isinstance(config, list):
        return list_to_comma_string(config)
    return str(config)


def list_to_comma_string(list_to_transform: list | str):
    return str(list_to_transform)[1:-1].replace("'", '')


def display_possible_values(config_name: str):
    possible_values = Configurations.get_possible_values_for(config_name)
    if possible_values:
        possible_values = format_config(possible_values)
        print(f'Possible values: {possible_values}')
