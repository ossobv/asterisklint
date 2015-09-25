from ..base import AppBase


class Answer(AppBase):
    pass


class BackGround(AppBase):
    pass


class Busy(AppBase):
    pass


class Congestion(AppBase):
    pass


class Goto(AppBase):
    pass


class GotoIf(AppBase):
    pass


class GotoIfTime(AppBase):
    pass


class ExecIfTime(AppBase):
    pass


class Hangup(AppBase):
    pass


class NoOp(AppBase):
    pass


class Proceeding(AppBase):
    pass


class Progress(AppBase):
    pass


class ResetCDR(AppBase):
    pass


class Ringing(AppBase):
    pass


class SayNumber(AppBase):
    pass


class SayDigits(AppBase):
    pass


class SayAlpha(AppBase):
    pass


class SayPhonetic(AppBase):
    pass


class SetAMAFlags(AppBase):
    pass


class SetGlobalVar(AppBase):
    pass


class Set(AppBase):
    pass


class ImportVar(AppBase):
    pass


class Wait(AppBase):
    pass


class WaitExten(AppBase):
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
