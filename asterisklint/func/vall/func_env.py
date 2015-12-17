from ..base import FuncBase


class ENV(FuncBase):
    pass


class FILE(FuncBase):
    pass


class FILE_COUNT_LINE(FuncBase):
    pass


class FILE_FORMAT(FuncBase):
    pass


class STAT(FuncBase):
    pass


def register(func_loader):
    for func in (
            ENV,
            FILE,
            FILE_COUNT_LINE,
            FILE_FORMAT,
            STAT,
            ):
        func_loader.register(func())
