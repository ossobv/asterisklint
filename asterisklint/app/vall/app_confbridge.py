from ..base import AppBase


class ConfBridge(AppBase):
    pass


def register(app_loader):
    app_loader.register(ConfBridge())
