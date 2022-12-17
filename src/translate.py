import logging
import sys
import traceback

from translating.argumentParsing.translatorCli import TranslatorCli
from translating.configs.configurations import Configurations
from translating.constants import Messages, Data
from translating.translatingPrinting.translationPrinter import TranslationPrinter


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
    except AttributeError as err:
        logging.error(traceback.format_exc())
        TranslationPrinter.out(Messages.ATTRIBUTE_ERROR)
    except Exception as ex:
        # TODO: in next((flag for flag in self._flags if flag.has_name(name))) of cli parser add an exception to know that the flag has not been added. Similarly in sibling cli_elements
        logging.exception(traceback.format_exc())
        TranslationPrinter.out(Messages.UNKNOWN_EXCEPTION)


def get_test_arguments():
    return 't sehen pl de -r'.split(' ')  # t laborious en uk


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
