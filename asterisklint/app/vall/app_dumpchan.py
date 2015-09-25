from ..base import AppBase


class DumpChan(AppBase):
    pass


def register(app_loader):
    app_loader.register(DumpChan())
