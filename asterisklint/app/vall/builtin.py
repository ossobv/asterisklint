from ..base import AppBase, IfStyleApp


class _Builtin(object):
    @property
    def module(self):
        return '<builtin>'


class BuiltinAppBase(_Builtin, AppBase):
    pass


class Answer(BuiltinAppBase):
    pass


class Background(BuiltinAppBase):
    # NOTE: It is called "BackGround" in Asterisk, but that makes my
    # eyes sore.
    pass


class Busy(BuiltinAppBase):
    pass


class Congestion(BuiltinAppBase):
    pass


class Goto(BuiltinAppBase):
    pass


class GotoIf(_Builtin, IfStyleApp):
    pass


class GotoIfTime(_Builtin, IfStyleApp):
    pass


class ExecIfTime(_Builtin, IfStyleApp):
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
            Answer, Background, Busy,
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
