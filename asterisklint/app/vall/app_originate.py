# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2018  Walter Doekes, OSSO B.V.
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
from ..base import E_APP_ARG_BADOPT, App, AppArg


class AppOrExten(AppArg):
    def validate(self, arg, where):
        if arg not in ('app', 'exten'):
            E_APP_ARG_BADOPT(
                where, argno=self.argno, app=self.app, opts=arg)


class Originate(App):
    def __init__(self):
        super().__init__(
            # arg1 means Application-name or Context
            args=[AppArg('tech_data'), AppOrExten('type'), AppArg('arg1'),
                  AppArg('arg2'), AppArg('arg3'), AppArg('timeout')],
            min_args=3)


def register(app_loader):
    app_loader.register(Originate())
