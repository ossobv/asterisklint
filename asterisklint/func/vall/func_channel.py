from ..base import FuncBase


class CHANNEL(FuncBase):
    pass


class CHANNELS(FuncBase):
    pass


class MASTER_CHANNEL(FuncBase):
    pass


def register(func_loader):
    for func in (
            CHANNEL,
            CHANNELS,
            MASTER_CHANNEL,
            ):
        func_loader.register(func())
