from ..base import FuncBase


class CURL(FuncBase):
    pass


class CURLOPT(FuncBase):
    pass


def register(func_loader):
    for func in (
            CURL, CURLOPT):
        func_loader.register(func())
