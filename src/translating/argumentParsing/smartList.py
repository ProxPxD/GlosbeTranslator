from __future__ import annotations

from collections.abc import Iterable
from types import GeneratorType


class SmartList(list):

    def __init__(self, to_list=None, limit=None):
        super().__init__()
        self._limit = limit
        if isinstance(to_list, (GeneratorType, map, Iterable)):
            to_list = list(to_list)
        if to_list:
            self.extend(to_list)

    def __iadd__(self, elems) -> SmartList:
        elems = [elems] if not isinstance(elems, Iterable) or isinstance(elems, str) else elems
        elems = self._remove_nones(elems)
        elems = self._cut_over_limit(elems)
        self._extend(elems)
        return self

    def _remove_nones(self, to_filter: Iterable):
        return [elem for elem in to_filter if elem is not None]

    def _cut_over_limit(self, to_cut: Iterable):
        return to_cut[:self._get_free_space()] if self._is_limited() else to_cut

    def __add__(self, x) -> SmartList:
        self.extend(x)
        return self

    def append(self, __object) -> None:
        self.__iadd__(__object)

    def extend(self, __iterable: Iterable) -> None:
        self.__iadd__(__iterable)

    def _append(self, __object) -> None:
        super(SmartList, self).append(__object)

    def _extend(self, __iterable: Iterable) -> None:
        super(SmartList, self).extend(__iterable)

    def _is_limited(self) -> bool:
        return self._limit is not None

    def _get_free_space(self):
        return self._limit - len(self)

    def __neg__(self):
        to_return = self[0] if len(self) else None
        if to_return:
            self.remove(to_return)
        return to_return
