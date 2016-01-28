from ..base import FuncBase


class SHELL(FuncBase):
    pass


def register(func_loader):
    func_loader.register(SHELL())
