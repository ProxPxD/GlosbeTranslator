import logging
import sys
from dataclasses import dataclass

from translating.argumentParsing.translatorParser import TranslatorCli
from translating.configs import configurations
from translating.configs.configurations import Configurations
from translating.constants import LogMessages
from translating.web.exceptions import WrongStatusCodeException


@dataclass(frozen=True)
class Data:
    LOG_PATH = configurations.Paths.RESOURCES_DIR / 'logs.txt'


def main():
    if len(sys.argv) == 1:
        sys.argv = get_test_arguments()

    try:
        Configurations.init()
        logging.basicConfig(filename=Data.LOG_PATH, encoding='utf-8', level=logging.WARNING, format='%(levelname)s: %(message)s ')
        argument_parser = TranslatorCli(sys.argv)
        argument_parser.parse()  # if not argument_parser.modes.is_any_displayable_mode_on():  #     Configurations.save()

    except WrongStatusCodeException as err:
        logging.error(f'{err.page.status_code}: {err.page.text}')
        print(LogMessages.UNKNOWN_PAGE_STATUS.format(
            err.page.status_code))  # except ParsingException as err:  #     for msg in err.validation_messages:  #         print(msg)


def get_test_arguments():
    return 't -la'.split(' ')  # t laborious en uk


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
