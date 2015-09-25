from ..base import AppBase


class ChanSpy(AppBase):
    pass


class ExtenSpy(AppBase):
    pass


def register(app_loader):
    app_loader.register(ChanSpy())
    app_loader.register(ExtenSpy())
