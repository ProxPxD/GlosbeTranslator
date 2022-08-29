from .abstractLayoutAdjuster import AbstractLayoutAdjuster


class KeyboardLayoutAdjuster(AbstractLayoutAdjuster):
    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        return {
            'uk': {
                'ут': 'en',
                'зд': 'pl',
                'ву': 'de',
                'ак': 'fr',
                'уі': 'es',
                'яр': 'zh',
                'гл': 'uk',
                'кг': 'ru',
                'ше': 'it',
                '-ц': '-w',
                '-ь': '-m',
                '-і': '-s',
                '-іі': '-ss',
                '-д': '-l',
                '-дд': '-ll',
                '-р': '-h',
            },
            'ru': {

            },
            'de': {
                'яр': 'yh',
            }
        }

