from ..base import AppBase


class CELGenUserEvent(AppBase):
    pass


def register(app_loader):
    app_loader.register(CELGenUserEvent())
