from typing import Any

from src.glosbe.cli.configurations import Configurations
from src.glosbe.cli.translatingPrinting.translationPrinter import TranslationPrinter


# TODO: move it in translator printer
class ConfigDisplayer:

    @classmethod
    def display_configs(cls, **config_names: str):
        for conf, value in config_names.items():
            cls.display_config(conf, value)

    @classmethod
    def display_config(cls, config_name: str, value: Any = None, show_possible=False):
        conf_to_display = value if value is not None else Configurations.get_conf(config_name)
        conf_to_display = cls.format_config(conf_to_display)
        TranslationPrinter.out(f'{config_name[2:]}: {conf_to_display}')

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
            TranslationPrinter.out(f'Possible values: {possible_values}')
