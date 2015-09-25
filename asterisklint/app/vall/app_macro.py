from ..base import AppBase


class Macro(AppBase):
    pass


class MacroIf(AppBase):
    pass


class MacroExclusive(AppBase):
    pass


class MacroExit(AppBase):
    pass


def register(app_loader):
    for app in (
            Macro, MacroIf, MacroExclusive, MacroExit):
        app_loader.register(app())
