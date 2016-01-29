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


class CHECKSIPDOMAIN(FuncBase):
    pass


class SIP_HEADER(FuncBase):
    pass


class SIPCHANINFO(FuncBase):
    pass


class SIPPEER(FuncBase):
    pass


def register(func_loader):
    for func in (
            CHECKSIPDOMAIN, SIP_HEADER,
            SIPCHANINFO, SIPPEER):
        func_loader.register(func())
