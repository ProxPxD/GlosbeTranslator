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


class Configurations:

    _configs: dict = None

    @staticmethod
    def init():
        if not Configurations._configs:
            Configurations._configs = Configurations._get_configurations()

    @staticmethod
    def _get_configurations() -> dict:
        with open(Paths.CONFIG_FILE, 'r') as f:
            configs = json.load(f)
        return configs

    @staticmethod
    def save():
        Configurations.__save(Configurations._configs)

    @staticmethod
    def save_and_close():
        Configurations.save()
        Configurations._configs = None

    @staticmethod
    def __save(configs: dict):
        with open(Paths.CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4, sort_keys=True)

    @staticmethod
    def init_default():
        Configurations.__save(Configurations.__get_default_config())

    @staticmethod
    def __get_default_config():
        return {
            Configs.MODE: '-s',
            Configs.LANG_LIMIT: 6,
            Configs.SAVED_LANGS: ['pl', 'en', 'es', 'ru', 'de', 'zh', 'fr']
        }

    @staticmethod
    def change_conf(conf: str, value):  # TODO: implement a config held in the memory to minimalize the calls. Possible a config singleton class
        if not Configurations._configs:
            Configurations.init()
        Configurations._configs[conf] = value

    @staticmethod
    def get_conf(name: str):
        return Configurations._configs[name]

    @staticmethod
    def save_last_used_languages(*langs):
        languages: list[str, ...] = Configurations.get_conf(Configs.SAVED_LANGS)
        for lang in langs:
            if lang in languages:
                languages.remove(lang)
                languages.insert(0, lang)
        Configurations.change_conf(Configs.SAVED_LANGS, languages)
