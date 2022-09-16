from src.translating.argumentParsing import constants


tupleLists = tuple[list[str], list[str]]


class WordDetector:

    def __init__(self):
        pass

    def is_word(self, to_test: str) -> bool:
        return len(to_test) > 3 or any(char not in constants.alphabet for char in to_test)

    def _membership(self, to_test):
        return 1 if self.is_word(to_test) else 0

    def split_to_langs_and_words(self, *to_tests: str) -> tupleLists:
        langs_words: tupleLists = ([], [])
        for to_test in to_tests:
            langs_words[self._membership(to_test)].append(to_test)

        return langs_words

    def put_in_right_list(self, to_test: str, langs: list[str], words: list[str], replace_from_other_list=False) -> tupleLists:
        langs_words: tupleLists = (langs, words)
        index = self._membership(to_test)
        langs_words[index].append(to_test)
        if replace_from_other_list:
            langs_words[1-index].append(langs_words[index][0])
        return langs_words

    def replace_input_if_word(self, langs_to_filter: list[str], words: list[str], fill_filtered_list: list = None):
        if fill_filtered_list is None:
            from_word_list = langs_to_filter
        #
        # pre_word_size = len(words)
        # not_langs = [to_filter for to_filter in langs_to_filter if self.is_word(to_filter)]
        # langs_to_filter = [to_filter for to_filter in langs_to_filter if not self.is_word(to_filter)]
        # words.extend(not_langs)
        # fill_filtered_list.extend()

