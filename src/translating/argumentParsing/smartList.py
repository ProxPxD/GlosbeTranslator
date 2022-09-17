from __future__ import annotations

from collections.abc import Iterable


class SmartList(list):

    def __init__(self, limit=None):
        self._limit = limit
        super().__init__()

    def __iadd__(self, elems) -> SmartList:
        if not isinstance(elems, Iterable):
            elems = [elem for elem in elems if elem is not None]
            if self._is_limited():
                elems = elems[:self._get_free_space()]
            self.extend(elems)
        elif elems is not None:
            self.append(elems)
        return self

    def __add__(self, x) -> SmartList:
        self.extend(x)
        return self

    def _is_limited(self) -> bool:
        return self._limit is not None

    def _get_free_space(self):
        return self._limit - len(self)

    def __neg__(self):
        to_return = self[0] if len(self) else None
        if to_return:
            self.remove(to_return)
        return to_return
