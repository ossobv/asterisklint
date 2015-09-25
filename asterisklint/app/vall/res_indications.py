from ..base import AppBase


class PlayTones(AppBase):
    pass


class StopPlayTones(AppBase):
    pass


def register(app_loader):
    for app in (
            PlayTones, StopPlayTones):
        app_loader.register(app())
