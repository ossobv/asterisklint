from ..base import AppBase


class MixMonitor(AppBase):
    pass


class StopMixMonitor(AppBase):
    pass


def register(app_loader):
    for app in (
            MixMonitor,
            StopMixMonitor,
            ):
        app_loader.register(app())
