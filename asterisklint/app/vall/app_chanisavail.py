from ..base import AppBase


class ChanIsAvail(AppBase):
    pass


def register(app_loader):
    app_loader.register(ChanIsAvail())
