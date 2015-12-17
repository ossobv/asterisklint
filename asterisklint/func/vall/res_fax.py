from ..base import FuncBase


class FAXOPT(FuncBase):
    pass


def register(func_loader):
    for func in (
            FAXOPT,
            ):
        func_loader.register(func())
