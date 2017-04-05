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
from asterisklint.alinttest import ALintTestCase
from asterisklint.variable import Var
from asterisklint.varfun import VarLoader
from asterisklint.where import DUMMY_WHERE


class SplitTest(ALintTestCase):
    def test_slice(self):
        var = VarLoader().parse_variables(
            '${${foo}:${start}:${len}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${${foo}:${start}:${len}}')

    def test_equals(self):
        var = VarLoader().parse_variables('foo=${bar}=baz', DUMMY_WHERE)
        data = var.split('=', 1)
        self.assertEqual(len(data), 2)
        variable, value = data
        self.assertTrue(isinstance(variable, str))
        self.assertTrue(isinstance(value, Var))
        self.assertEqual(value.format(bar='BAR'), 'BAR=baz')

    def test_writefunc(self):
        # TODO: overly complicated internals here; please fix
        var = VarLoader().parse_variables('FUNC(${bar},baz)', DUMMY_WHERE)
        data = var.split('(', 1)
        self.assertEqual(len(data), 2)
        variable, value = data
        self.assertTrue(isinstance(variable, str))
        self.assertTrue(isinstance(value, Var))
        self.assertEqual(value[-1], ')')
        value = Var.join(value[0:-1])
        self.assertEqual(value.format(bar='BAR'), 'BAR,baz')
