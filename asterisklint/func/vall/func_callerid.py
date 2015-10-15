from ..base import FuncBase


class CALLERID(FuncBase):
    pass


class CALLERPRES(FuncBase):
    pass


class CONNECTEDLINE(FuncBase):
    pass


class REDIRECTING(FuncBase):
    pass


def register(func_loader):
    for func in (
            CALLERID,
            CALLERPRES,
            CONNECTEDLINE,
            REDIRECTING,
            ):
        func_loader.register(func())
