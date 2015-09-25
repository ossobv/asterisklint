from ..base import AppBase


class Read(AppBase):
    pass


def register(app_loader):
    for app in (
            Read,
            ):
        app_loader.register(app())
