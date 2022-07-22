import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent  # Path("/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations")
    RESOURCES_DIR = WORKING_DIR / 'resources'
    CONFIG_FILE = WORKING_DIR / 'configurations.txt'
    LAST_USED_LANGUAGES = WORKING_DIR / 'languages.txt'


def init():
    __save(__get_default_config())


def __get_default_config():
    return {
        "language_limit": 6,
        "mode": "single"
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