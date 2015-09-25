from ..base import AppBase


class MusicOnHold(AppBase):
    pass


class WaitMusicOnHold(AppBase):
    pass


class SetMusicOnHold(AppBase):
    pass


class StartMusicOnHold(AppBase):
    pass


class StopMusicOnHold(AppBase):
    pass


def register(app_loader):
    for app in (
            MusicOnHold, WaitMusicOnHold, SetMusicOnHold,
            StartMusicOnHold, StartMusicOnHold):
        app_loader.register(app())
