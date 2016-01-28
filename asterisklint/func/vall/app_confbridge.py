from ..base import FuncBase


class CONFBRIDGE(FuncBase):
    pass


class CONFBRIDGE_INFO(FuncBase):
    pass


def register(func_loader):
    for func in (
            CONFBRIDGE,
            CONFBRIDGE_INFO,
            ):
        func_loader.register(func())
