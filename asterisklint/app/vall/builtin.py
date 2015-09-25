from ..base import AppBase


class BuiltinAppBase(AppBase):
    @property
    def module(self):
        return '<builtin>'


class Answer(BuiltinAppBase):
    pass


class BackGround(BuiltinAppBase):
    pass


class Busy(BuiltinAppBase):
    pass


class Congestion(BuiltinAppBase):
    pass


class Goto(BuiltinAppBase):
    pass


class GotoIf(BuiltinAppBase):
    pass


class GotoIfTime(BuiltinAppBase):
    pass


class ExecIfTime(BuiltinAppBase):
    pass


class Hangup(BuiltinAppBase):
    pass


class NoOp(BuiltinAppBase):
    pass


class Proceeding(BuiltinAppBase):
    pass


class Progress(BuiltinAppBase):
    pass


class ResetCDR(BuiltinAppBase):
    pass


class Ringing(BuiltinAppBase):
    pass


class SayNumber(BuiltinAppBase):
    pass


class SayDigits(BuiltinAppBase):
    pass


class SayAlpha(BuiltinAppBase):
    pass


class SayPhonetic(BuiltinAppBase):
    pass


class SetAMAFlags(BuiltinAppBase):
    pass


class SetGlobalVar(BuiltinAppBase):
    pass


class Set(BuiltinAppBase):
    pass


class ImportVar(BuiltinAppBase):
    pass


class Wait(BuiltinAppBase):
    pass


class WaitExten(BuiltinAppBase):
    pass


def register(app_loader):
    for app in (
            Answer, BackGround, Busy,
            Congestion, Goto, GotoIf,
            GotoIfTime, ExecIfTime,
            Hangup, NoOp, Proceeding,
            Progress, ResetCDR, Ringing,
            SayNumber, SayDigits, SayAlpha,
            SayPhonetic, SetAMAFlags,
            SetGlobalVar, Set,
            ImportVar, Wait,
            WaitExten):
        app_loader.register(app())
