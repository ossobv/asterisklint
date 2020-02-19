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


class PJSIP_AOR(FuncBase):
    # func_pjsip_aor.so
    pass


class PJSIP_CONTACT(FuncBase):
    # func_pjsip_contact.so
    pass


class PJSIP_ENDPOINT(FuncBase):
    # func_pjsip_endpoint.so
    pass


def register(func_loader):
    for func in (
            PJSIP_AOR,
            PJSIP_CONTACT,
            PJSIP_ENDPOINT,
            ):
        func_loader.register(func())
