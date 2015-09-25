from ..base import AppBase


class SetCallerID(AppBase):
    pass


class SetCallerPres(AppBase):
    pass


def register(app_loader):
    for app in (
            SetCallerID,
            SetCallerPres,
            ):
        app_loader.register(app())
