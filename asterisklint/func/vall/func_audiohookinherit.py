# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2017  Walter Doekes, OSSO B.V.
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
from .. import E_FUNC_BAD_ARGS
from ..base import FuncBase


class AUDIOHOOK_INHERIT(FuncBase):
    def __call__(self, data, where):
        if isinstance(data, str) and data not in (
                'MixMonitor', 'Chanspy', 'Volume', 'Speex',
                'pitch_shift', 'JACK_HOOK', 'Mute'):
            E_FUNC_BAD_ARGS(where, func=self.name, data=data)

        super().__call__(data, where)


def register(func_loader):
    func_loader.register(AUDIOHOOK_INHERIT())
