from ..base import AppBase


class Playback(AppBase):
    pass


def register(app_loader):
    app_loader.register(Playback())
