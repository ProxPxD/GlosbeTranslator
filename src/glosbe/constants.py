from dataclasses import dataclass

from .cli.configs import configurations


@dataclass(frozen=True)
class Data:
    LOG_PATH = configurations.Paths.RESOURCES_DIR / 'logs.txt'

