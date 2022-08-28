from .abstractScriptAdjuster import AbstractScriptAdjuster
from .nativeScriptAdjuster import NativeScriptAdjuster
from ..configurations import Configurations, Configs
from ..constants import LanguageSpecificAdjustmentValues

_adjusters = {
        LanguageSpecificAdjustmentValues.NATIVE: NativeScriptAdjuster,
    }


def get_script_adjuster(type: str, lang: str = None) -> AbstractScriptAdjuster:
    if not lang:
        lang: str = Configurations.get_conf(Configs.ADJUSTMENT_LANG)
    return _adjusters[type](lang) if type in _adjusters else None