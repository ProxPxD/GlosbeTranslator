from dataclasses import dataclass

from .cli.configs import configurations


@dataclass(frozen=True)
class Data:
    LOG_PATH = configurations.Paths.RESOURCES_DIR / 'logs.txt'


@dataclass(frozen=True)
class Messages:

    @dataclass(frozen=True)
    class ErrorMessages:
        NO_TRANSLATION: str = 'No translation has been found. Either the arguments were invalid or the requested translation does not exist so far'
        UNKNOWN_EXCEPTION: str = 'Unknown exception occurred!'
        ATTRIBUTE_ERROR: str = 'Error! Please send logs to the creator'