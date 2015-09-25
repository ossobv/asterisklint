from ..base import AppBase


class Exec(AppBase):
    pass


class ExecIf(AppBase):
    pass


class TryExec(AppBase):
    pass


def register(app_loader):
    for app in (
            Exec, ExecIf, TryExec):
        app_loader.register(app())
