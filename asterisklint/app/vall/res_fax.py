from ..base import AppBase


class ReceiveFAX(AppBase):
    pass


class SendFAX(AppBase):
    pass


def register(app_loader):
    for app in (
            ReceiveFAX, SendFAX):
        app_loader.register(app())
