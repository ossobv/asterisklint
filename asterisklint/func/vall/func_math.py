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
from ..base import FuncBase
from ...varfun import VarLoader


class MATH(FuncBase):
    pass


class INC(FuncBase):
    """
    INC takes a single varname as argument. That means we can count the
    variable as used.
    """
    def __call__(self, data, where):
        ret = super().__call__(data, where)
        VarLoader().count_var(data, where)
        return ret


class DEC(FuncBase):
    """
    DEC takes a single varname as argument. That means we can count the
    variable as used.
    """
    def __call__(self, data, where):
        ret = super().__call__(data, where)
        VarLoader().count_var(data, where)
        return ret


def register(func_loader):
    for func in (
            MATH, INC, DEC):
        func_loader.register(func())
