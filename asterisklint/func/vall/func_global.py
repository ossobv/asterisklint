from ..base import FuncBase


class GLOBAL(FuncBase):
    pass


class SHARED(FuncBase):
    pass


def register(func_loader):
    for func in (
            GLOBAL, SHARED):
        func_loader.register(func())
