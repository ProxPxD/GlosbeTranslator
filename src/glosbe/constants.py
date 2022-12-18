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

    @dataclass(frozen=True)
    class PageCodeMessages:
        PLEASE_REPORT: str = 'Please, report the case'
        UNHANDLED_PAGE_FULL_MESSAGE: str = 'Unhandled page code: {}! ' + PLEASE_REPORT
        PAGE_NOT_FOUND_404: str = 'Page has not been found (404). Please, check the arguments: {}'  # if the command is correct. Words: {}, glosbe from: , glosbe to:
        PAGE_NOT_FOUND_303: str = 'The page has to be redirected (303). ' + PLEASE_REPORT