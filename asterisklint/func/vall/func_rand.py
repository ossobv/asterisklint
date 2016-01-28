from ..base import FuncBase


class RAND(FuncBase):
    pass


def register(func_loader):
    func_loader.register(RAND())
