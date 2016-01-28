from ..base import AppBase


class DateTime(AppBase):
    pass


class SayUnixTime(AppBase):
    pass


def register(app_loader):
    for app in (
            DateTime, SayUnixTime):
        app_loader.register(app())
