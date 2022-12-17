import unittest

from tests.abstractTest import AbstractTest
from tests.flagSettingTest import FlagSettingTest
from tests.formattingTest import FormattingTest
from tests.helpTest import HelpTest
from tests.misplacedTest import MisplacedTest
from tests.multiLangTranslationTest import MultiLangCliTest
from tests.multiWordTranslationTest import MultiWordCliTest
from tests.singleTranslationTest import SingleModeCliTest

tests = [
    SingleModeCliTest,
    MultiLangCliTest,
    MultiWordCliTest,
    MisplacedTest,
    FormattingTest,
    HelpTest,
    FlagSettingTest,
]


def main():
    failure, errors, total, skipped = 0, 0, 0, 0
    for test_class in tests:
        test = test_class()
        unittest.main(module=test, exit=False)

        failure += test.failure
        errors += test.errors
        total += test.total
        skipped += test.skipped

    print()
    print('#' * (2 * AbstractTest.half_sep_length))
    print('Total test statistics:')
    AbstractTest.print_statistics(failure, errors, skipped, total)


if __name__ == '__main__':
    main()