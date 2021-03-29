# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2020  Walter Doekes, OSSO B.V.
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


class PJSIP_DIAL_CONTACTS(FuncBase):
    pass


class PJSIP_DTMF_MODE(FuncBase):
    pass


class PJSIP_MEDIA_OFFER(FuncBase):
    pass


class PJSIP_MOH_PASSTHROUGH(FuncBase):
    pass


class PJSIP_PARSE_URI(FuncBase):
    pass


class PJSIP_SEND_SESSION_REFRESH(FuncBase):
    pass


def register(func_loader):
    for func in (
            PJSIP_DIAL_CONTACTS,
            PJSIP_DTMF_MODE,
            PJSIP_MEDIA_OFFER,
            PJSIP_MOH_PASSTHROUGH,
            PJSIP_PARSE_URI,
            PJSIP_SEND_SESSION_REFRESH,
            ):
        func_loader.register(func())
