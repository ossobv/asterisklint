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
from asterisklint.alinttest import ALintTestCase
from asterisklint.defines import WarningDef
from asterisklint.where import DUMMY_WHERE


class MessageTestCase(ALintTestCase):
    def test_normal(self):
        class W_WARNING1(WarningDef):
            message = 'irrelevant'

        W_WARNING1(DUMMY_WHERE)
        self.assertLinted({'W_WARNING1': 1})

    def test_format_required(self):
        class W_WARNING2(WarningDef):
            message = '{message} with {format}'

        # Properly formatted.
        W_WARNING2(DUMMY_WHERE, format='cheese', message='sandwitch')

        # Missing formats.
        self.assertRaises(
            KeyError,
            W_WARNING2, DUMMY_WHERE, message='sandwitch')

        self.assertLinted({'W_WARNING2': 2})
