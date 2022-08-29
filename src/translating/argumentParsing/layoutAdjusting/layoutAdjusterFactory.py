from .abstractLayoutAdjuster import AbstractLayoutAdjuster
from .keyboardLayoutAdjuster import KeyboardLayoutAdjuster
from .nativeLayoutAdjuster import NativeLayoutAdjuster
from ..configurations import Configurations, Configs
from ..constants import LanguageSpecificAdjustmentValues

_adjusters = {
        LanguageSpecificAdjustmentValues.NATIVE: NativeLayoutAdjuster,
        LanguageSpecificAdjustmentValues.KEYBOARD: KeyboardLayoutAdjuster,
    }


def get_layout_adjuster(type: str, lang: str = None) -> AbstractLayoutAdjuster:
    if not lang:
        lang: str = Configurations.get_conf(Configs.ADJUSTMENT_LANG)
    return _adjusters[type](lang) if type in _adjusters else None