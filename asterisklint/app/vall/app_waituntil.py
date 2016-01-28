from ..base import AppBase


class WaitUntil(AppBase):
    pass


def register(app_loader):
    app_loader.register(WaitUntil())
