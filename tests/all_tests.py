import unittest

from tests.multiLangTranslationTest import MultiLangTranslationTest
from tests.multiWordTranslationTest import MultiWordTranslationTest
from tests.singleTranslationTest import SingleTranslationTest
from tests.misplacedTest import MisplacedTest

tests = [
    SingleTranslationTest,
    MultiLangTranslationTest,
    MultiWordTranslationTest,
    MisplacedTest,
]


def main():
    for test_class in tests:
        test = test_class()
        unittest.main(module=test, exit=False)


if __name__ == '__main__':
    main()