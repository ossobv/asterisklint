from ..base import AppBase


class Gosub(AppBase):
    pass


class GosubIf(AppBase):
    pass


class Return(AppBase):
    pass


class StackPop(AppBase):
    pass


def register(app_loader):
    for app in (
            Gosub, GosubIf, Return, StackPop):
        app_loader.register(app())
