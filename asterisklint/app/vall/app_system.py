from ..base import AppBase


class System(AppBase):
    pass


class TrySystem(AppBase):
    pass


def register(app_loader):
    for app in (
            System,
            TrySystem,
            ):
        app_loader.register(app())
