from ..base import AppBase


class Echo(AppBase):
    pass


def register(app_loader):
    for app in (
            Echo,
            ):
        app_loader.register(app())
