from ..base import FuncBase


class CDR(FuncBase):
    pass


def register(func_loader):
    for func in (
            CDR,
            ):
        func_loader.register(func())
