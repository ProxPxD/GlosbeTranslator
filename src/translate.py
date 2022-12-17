import logging
import sys
import traceback
from dataclasses import dataclass

from translating.argumentParsing.translatorCli import TranslatorCli
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
        cli = TranslatorCli(sys.argv)
        cli.parse()  # if not argument_parser.modes.is_any_displayable_mode_on():  #     Configurations.save()
        Configurations.change_last_used_languages(*cli.langs)
        Configurations.save_and_close()
    except WrongStatusCodeException as err:
        logging.error(f'{err.page.status_code}: {err.page.text}')
        print(LogMessages.UNKNOWN_PAGE_STATUS.format(err.page.status_code))  # except ParsingException as err:  #     for msg in err.validation_messages:  #         print(msg)
    except Exception as ex:
        print('Exception occured!')
        trace_back = traceback.format_exc()
        logging.exception(trace_back)


def get_test_arguments():
    return 't pl -m ar la zh fr -w mieć być spać'.split(' ')  # t laborious en uk


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
