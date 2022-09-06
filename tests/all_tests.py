import unittest

from tests.multiLangTranslationTest import MultiLangTranslationTest
from tests.multiWordTranslationTest import MultiWordTranslationTest
from tests.singleTranslationTest import SingleTranslationTest

tests = [
    SingleTranslationTest,
    MultiLangTranslationTest,
    MultiWordTranslationTest,
]


def main():
    unittest.main(exit=False, verbosity=0)

# python -m unittest discover -s tests -p *Test.py

if __name__ == '__main__':
    main()