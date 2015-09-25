from ..base import AppBase


class Unknown(AppBase):
    pass


def register(app_loader):
    app_loader.register(Unknown())
