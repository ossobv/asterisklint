from ..base import AppBase


class Page(AppBase):
    pass


def register(app_loader):
    for app in (
            Page,
            ):
        app_loader.register(app())
