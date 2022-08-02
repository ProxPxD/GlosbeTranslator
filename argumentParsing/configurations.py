import json
from dataclasses import dataclass
from pathlib import Path

from argumentParsing.modeManager import FullModes


@dataclass(frozen=True)
class Paths:
    WORKING_DIR = Path(__file__).parent.parent  # Path("/home/proxpxd/Desktop/moje_programy/systemowe/glosbeTranslations")
    RESOURCES_DIR = WORKING_DIR / 'resources'
    CONFIG_FILE = RESOURCES_DIR / 'configurations.txt'


class Configs:
    DEFAULT_TRANSLATIONAL_MODE: str = FullModes.DEFAULT_TRANSLATIONAL_MODE
    LANG_LIMIT: str = FullModes.LANG_LIMIT
    SAVED_LANGS: str = FullModes.SAVED_LANGS


class Configurations:

    _configs: dict = None

    @staticmethod
    def init():
        if not Configurations._configs:
            if not Paths.CONFIG_FILE.exists():
                Configurations.init_default()
            Configurations._configs = Configurations._get_configurations()

    @staticmethod
    def _get_configurations() -> dict:
        with open(Paths.CONFIG_FILE, 'r') as f:
            configs = json.load(f)
        return configs

    @staticmethod
    def save():
        Configurations._save(Configurations._configs)

    @staticmethod
    def save_and_close():
        Configurations.save()
        Configurations._configs = None

    @staticmethod
    def _save(configs: dict):
        with open(Paths.CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4, sort_keys=True)

    @staticmethod
    def init_default():
        Configurations._save(Configurations.__get_default_config())

    @staticmethod
    def __get_default_config():
        return {
            Configs.DEFAULT_TRANSLATIONAL_MODE: '-s',
            Configs.LANG_LIMIT: 6,
            Configs.SAVED_LANGS: ['pl', 'en', 'es', 'ru', 'de', 'zh', 'fr']
        }

    @staticmethod
    def change_conf(conf: str, value):
        if not Configurations._configs:
            Configurations.init()
        Configurations._configs[conf] = value

    @staticmethod
    def get_conf(name: str):
        return Configurations._configs[name]

    @staticmethod
    def get_saved_languages() -> list[str]:
        return Configurations.get_conf(Configs.SAVED_LANGS)

    @staticmethod
    def get_nth_saved_language(index: int) -> str:
        return Configurations.get_saved_languages()[index]

    @staticmethod
    def load_config_languages(to_skip: str = None):
        langs: list = Configurations.get_conf(Configs.SAVED_LANGS)
        limit: int = Configurations.get_conf(Configs.LANG_LIMIT)
        if to_skip:
            langs.remove(to_skip)
        if limit is not None and len(langs) > limit:
            langs = langs[:limit]
        return langs

    @staticmethod
    def save_last_used_languages(*langs):
        languages: list[str] = Configurations.get_conf(Configs.SAVED_LANGS)
        for lang in langs:
            if lang in languages:
                languages.remove(lang)
                languages.insert(0, lang)
        Configurations.change_conf(Configs.SAVED_LANGS, languages)
