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


class ARRAY(FuncBase):
    pass


class CSV_QUOTE(FuncBase):
    pass


class EVAL(FuncBase):
    pass


class FIELDNUM(FuncBase):
    pass


class FIELDQTY(FuncBase):
    pass


class FILTER(FuncBase):
    pass


class HASH(FuncBase):
    pass


class HASHKEYS(FuncBase):
    pass


class KEYPADHASH(FuncBase):
    pass


class LEN(FuncBase):
    pass


class LISTFILTER(FuncBase):
    pass


class PASSTHRU(FuncBase):
    pass


class POP(FuncBase):
    pass


class PUSH(FuncBase):
    pass


class QUOTE(FuncBase):
    pass


class REGEX(FuncBase):
    pass


class REPLACE(FuncBase):
    pass


class SHIFT(FuncBase):
    pass


class STRFTIME(FuncBase):
    pass


class STRPTIME(FuncBase):
    pass


class STRREPLACE(FuncBase):
    pass


class TOLOWER(FuncBase):
    pass


class TOUPPER(FuncBase):
    pass


class UNSHIFT(FuncBase):
    pass


def register(func_loader):
    for func in (
            ARRAY,
            CSV_QUOTE,
            EVAL,
            FIELDNUM,
            FIELDQTY,
            FILTER,
            HASH,
            HASHKEYS,
            KEYPADHASH,
            LEN,
            LISTFILTER,
            PASSTHRU,
            POP,
            PUSH,
            QUOTE,
            REGEX,
            REPLACE,
            SHIFT,
            STRFTIME,
            STRPTIME,
            STRREPLACE,
            TOLOWER,
            TOUPPER,
            UNSHIFT,
            ):
        func_loader.register(func())
