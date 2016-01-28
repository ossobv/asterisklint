from ..base import FuncBase


class URIDECODE(FuncBase):
    pass


class URIENCODE(FuncBase):
    pass


def register(func_loader):
    for func in (
            URIDECODE,
            URIENCODE,
            ):
        func_loader.register(func())
