from typing import Any

from .configurations import Configurations


#
# def display_information(argument_parser: TranslatorParser):
#     for to_display in argument_parser.modes.get_modes_turned_on_by_type(ModeTypes.DISPLAYABLE):
#         if to_display == FLAGS.SETTINGS:
#             display_configs(FLAGS.DEFAULT_TRANSLATIONAL_MODE, FLAGS.LANG_LIMIT,
#                             FLAGS.SAVED_LANGS, FLAGS.ADJUSTMENT_LANG, FLAGS.LAYOUT_ADJUSTMENT_MODE)
#             continue
#         if to_display == FLAGS.HELP:
#             FlagsManager.show_help()
#             continue
#         display_config(to_display, show_possible=True)


class ConfigDisplayer:

    out = print

    @classmethod
    def display_configs(cls, **config_names: str):  # TODO: implement help and input modes validation
        for conf, value in config_names.items():
            cls.display_config(conf, value)

    @classmethod
    def display_config(cls, config_name: str, value: Any = None, show_possible=False):
        conf_to_display = value if value is not None else Configurations.get_conf(config_name)
        conf_to_display = cls.format_config(conf_to_display)
        cls.out(f'{config_name[2:]}: {conf_to_display}')

        if show_possible:
            cls.display_possible_values(config_name)

    @classmethod
    def format_config(cls, config: list | str):
        if isinstance(config, list):
            return cls.list_to_comma_string(config)
        return str(config)

    @classmethod
    def list_to_comma_string(cls, list_to_transform: list | str):
        return str(list_to_transform)[1:-1].replace("'", '')

    @classmethod
    def display_possible_values(cls, config_name: str):
        possible_values = Configurations.get_possible_values_for(config_name)
        if possible_values:
            possible_values = cls.format_config(possible_values)
            cls.out(f'Possible values: {possible_values}')
