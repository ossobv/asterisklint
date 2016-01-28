from ..base import AppBase


class UserEvent(AppBase):
    pass


def register(app_loader):
    app_loader.register(UserEvent())
