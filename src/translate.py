import logging
import shlex
import sys
import traceback
from dataclasses import dataclass

from glosbe.configurations import Configurations, Paths
from glosbe.translatingPrinting.translationPrinter import TranslationPrinter
from glosbe.translatorCli import TranslatorCli
from src.glosbe.translating.scrapping import Scrapper


@dataclass(frozen=True)
class ErrorMessages:
    UNKNOWN_EXCEPTION: str = 'Unknown exception occurred!'
    ATTRIBUTE_ERROR: str = 'Error! Please send logs to the creator'


@dataclass(frozen=True)
class Data:
    LOG_PATH = Paths.RESOURCES_DIR / 'logs.txt'


def main():
    if len(sys.argv) == 1:
        sys.argv = get_test_arguments()

    try:
        Configurations.init()
        logging.basicConfig(filename=Data.LOG_PATH, encoding='utf-8', level=logging.WARNING, format='%(levelname)s: %(message)s ')
        cli = TranslatorCli(sys.argv)
        cli.parse()
        Configurations.change_last_used_languages(*cli.langs)
        Configurations.save_and_close()
    except AttributeError as err:
        logging.error(traceback.format_exc())
        TranslationPrinter.out(ErrorMessages.ATTRIBUTE_ERROR)
    except Exception as ex:
        # TODO: in next((flag for flag in self._flags if flag.has_name(name))) of cli parser add an exception to know that the flag has not been added. Similarly in sibling cli_elements
        logging.exception(traceback.format_exc())
        TranslationPrinter.out(ErrorMessages.UNKNOWN_EXCEPTION)


def get_test_arguments():
    return shlex.split('t pl -w wyspa rzeka woda -m sv nb da')
    # TODO: add test for no saved lang exception
    # TODO: t anomic en pl
    # TODO: add test for mis_tok


if __name__ == '__main__':
    try:
        scrapper = Scrapper()
        res = scrapper.scrap_conjugation('pl', 'dać')  # mieć
        res = list(res)

        # main()
    except KeyboardInterrupt:
        pass
