from ..base import FuncBase


class UNKNOWN(FuncBase):
    pass


def register(func_loader):
    func_loader.register(UNKNOWN())
