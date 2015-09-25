from ..base import AppBase


class Log(AppBase):
    pass


class Verbose(AppBase):
    pass


def register(app_loader):
    app_loader.register(Log())
    app_loader.register(Verbose())
