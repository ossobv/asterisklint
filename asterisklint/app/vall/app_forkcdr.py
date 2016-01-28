from ..base import AppBase


class ForkCDR(AppBase):
    pass


def register(app_loader):
    app_loader.register(ForkCDR())
