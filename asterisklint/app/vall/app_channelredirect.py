from ..base import AppBase


class ChannelRedirect(AppBase):
    pass


def register(app_loader):
    for app in (
            ChannelRedirect,
            ):
        app_loader.register(app())
