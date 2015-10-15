from ..base import FuncBase


class CUT(FuncBase):
    pass


class SORT(FuncBase):
    pass


def register(func_loader):
    for func in (
            CUT,
            SORT,
            ):
        func_loader.register(func())
