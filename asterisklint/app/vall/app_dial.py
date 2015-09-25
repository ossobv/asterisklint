from ..base import AppBase


class Dial(AppBase):
    pass


class RetryDial(AppBase):
    pass


def register(app_loader):
    app_loader.register(Dial())
    app_loader.register(RetryDial())
