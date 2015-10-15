from ..base import FuncBase


class EXISTS(FuncBase):
    pass


class IF(FuncBase):
    pass


class IFTIME(FuncBase):
    pass


class IMPORT(FuncBase):
    pass


class ISNULL(FuncBase):
    pass


class SET(FuncBase):
    pass


def register(func_loader):
    for func in (
            EXISTS,
            IF,
            IFTIME,
            IMPORT,
            ISNULL,
            SET,
            ):
        func_loader.register(func())
