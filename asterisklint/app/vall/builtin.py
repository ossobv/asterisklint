# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2016  Walter Doekes, OSSO B.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from ..base import (
    AppBase, DelimitedArgsMixin, IfStyleApp, MinMaxArgsMixin,
    NoPipeDelimiterMixin, VarCondIfStyleApp)


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


class Goto(_Builtin, NoPipeDelimiterMixin, MinMaxArgsMixin, DelimitedArgsMixin,
           AppBase):
    def __init__(self, **kwargs):
        super().__init__(min_args=1, max_args=3, **kwargs)

    def __call__(self, data, where, jump_destinations):
        args = super().__call__(data, where, jump_destinations)

        jumpdest = args[:]
        while len(jumpdest) != 3:
            jumpdest.insert(0, None)
        assert len(jumpdest) == 3
        jump_destinations.append(tuple(jumpdest))

        return args


class GotoIf(_Builtin, VarCondIfStyleApp):
    def __call__(self, data, where, jump_destinations):
        cond, iftrue, iffalse = super().__call__(
            data, where, jump_destinations)

        for args in (iftrue, iffalse):
            if args:
                jumpdest = self.separate_args(args)
                while len(jumpdest) != 3:
                    jumpdest.insert(0, None)
                assert len(jumpdest) == 3
                jump_destinations.append(tuple(jumpdest))

        return cond, iftrue, iffalse


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
