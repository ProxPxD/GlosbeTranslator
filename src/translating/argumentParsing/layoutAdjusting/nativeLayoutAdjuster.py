from .abstractLayoutAdjuster import AbstractLayoutAdjuster


class NativeLayoutAdjuster(AbstractLayoutAdjuster):

    def _get_dictionary(self) -> dict[str, dict[str, str]]:
        return {
            'uk': {
                'ен': 'en',
                'пл': 'pl',
                'де': 'de',
                'фр': 'fr',
                'ес': 'es',
                'дж': 'zh',
                'ук': 'uk',
                'ру': 'ru',
                'іт': 'it',
            },
            'ru': {
                'ен': 'en',
                'пл': 'pl',
                'де': 'de',
                'фр': 'fr',
                'ес': 'es',
                'дж': 'zh',
                'ук': 'uk',
                'ру': 'ru',
                'ит': 'it',
            },
            'zh': {
                '英': 'en',
                '波': 'pl',
                '德': 'de',
                '法': 'fr',
                '西': 'es',
                '中': 'zh',
                '乌': 'uk',
                '俄': 'ru',
                '意': 'it',
            },
        }
