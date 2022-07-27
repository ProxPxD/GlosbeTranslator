import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent  # Path("/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations")
    RESOURCES_DIR = WORKING_DIR / 'resources'
    CONFIG_FILE = WORKING_DIR / 'configurations.txt'
    LAST_USED_LANGUAGES = WORKING_DIR / 'languages.txt'


class Configs:
    MODE: str = 'mode'
    LANG_LIMIT: str = 'lang_limit'
    SAVED_LANGS: str = 'saved_langs'


def init():
    __save(__get_default_config())


def __get_default_config():
    return {
        Configs.MODE: '-s',
        Configs.LANG_LIMIT: 6,
        Configs.SAVED_LANGS: ['pl', 'en', 'es', 'ru', 'de', 'zh', 'fr']
    }


def change_conf(conf: str, value):  # TODO: implement a config held in the memory to minimalize the calls. Possible a config singleton class
    __change_configs([conf], [value])

def __change_configs(confs: list[str, ...], values: list[Any, ...]):
    configs = get_configurations()
    for conf, value in zip(confs, values):
        configs[conf] = value
    __save(configs)


def get_configurations() -> dict:
    with open(Paths.CONFIG_FILE, 'r') as f:
        configs = json.load(f)
    return configs


def get_conf(name: str):
    return get_configurations()[name]


def save_last_used_languages(*langs):
    languages: list[str, ...] = get_conf(Configs.SAVED_LANGS)
    for lang in langs:
        languages.remove(lang)
        languages.insert(0, lang)
    change_conf(Configs.SAVED_LANGS, languages)


def __save(configs: dict):
    with open(Paths.CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=4, sort_keys=True)