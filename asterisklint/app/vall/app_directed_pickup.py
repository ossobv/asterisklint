from ..base import AppBase


class Pickup(AppBase):
    pass


def register(app_loader):
    for app in (
            Pickup,
            ):
        app_loader.register(app())
