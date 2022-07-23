import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent  # Path("/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations")
    RESOURCES_DIR = WORKING_DIR / 'resources'
    CONFIG_FILE = WORKING_DIR / 'configurations.txt'
    LAST_USED_LANGUAGES = WORKING_DIR / 'languages.txt'


class Configs:
    MODE: str = 'mode'
    FROM_LANG: str = 'from_lang'
    TO_LANG: str = 'to_lang'
    LANG_LIMIT: str = 'lang_limit'


def init():
    __save(__get_default_config())


def __get_default_config():
    return {
        Configs.MODE: '-s',
        Configs.LANG_LIMIT: 6
    }


def change_conf(conf: dict, value):
    configs = get_configurations()
    configs[conf] = value
    __save(configs)


def get_configurations() -> dict:
    with open(Paths.CONFIG_FILE, 'r') as f:
        configs = json.load(f)
    return configs


def get_conf(name: str):
    return get_configurations()[name]


def __save(configs: dict):
    with open(Paths.CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=4, sort_keys=True)