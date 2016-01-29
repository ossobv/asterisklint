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
from asterisklint.varfun import VarLoader
from asterisklint.variable import Var
from asterisklint.where import DUMMY_WHERE


class SubstringTest(ALintTestCase):
    def test_var_begin(self):
        var = VarLoader().parse_variables('${foo:0:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=0, length=2))
        self.assertEqual(
            str(var), '${foo:0:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'AB')

    def test_var_offset(self):
        var = VarLoader().parse_variables('${foo:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=2))
        self.assertEqual(
            str(var), '${foo:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'CDEF')

    def test_var_middle(self):
        var = VarLoader().parse_variables('${foo:2:3}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=2, length=3))
        self.assertEqual(
            str(var), '${foo:2:3}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'CDE')

    def test_var_end(self):
        var = VarLoader().parse_variables('${foo:-2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=-2))
        self.assertEqual(
            str(var), '${foo:-2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'EF')

    def test_var_neg1_end(self):
        var = VarLoader().parse_variables('${foo:1:-1}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=1, length=-1))
        self.assertEqual(
            str(var), '${foo:1:-1}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'BCDE')

    def test_var_neg2_end(self):
        var = VarLoader().parse_variables('${foo:1:-2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=1, length=-2))
        self.assertEqual(
            str(var), '${foo:1:-2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'BCD')

    def test_var_endmiddle(self):
        var = VarLoader().parse_variables('${foo:-3:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=-3, length=2))
        self.assertEqual(
            str(var), '${foo:-3:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'DE')

    def test_invalid_args(self):
        VarLoader().parse_variables('${foo:1:2:3}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_ARGS': 1})

    def test_invalid_start(self):
        # blank
        VarLoader().parse_variables('${foo:}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # garbage
        VarLoader().parse_variables('${foo:x}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # 0-offset
        VarLoader().parse_variables('${foo:0}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # blank with length
        VarLoader().parse_variables('${foo::2}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

    def test_invalid_length(self):
        # blank
        VarLoader().parse_variables('${foo:0:}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # garbage
        VarLoader().parse_variables('${foo:0:x}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # 0-length
        VarLoader().parse_variables('${foo:2:0}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # length as large as negative offset
        VarLoader().parse_variables('${foo:-2:1}', DUMMY_WHERE)  # ok
        self.assertLinted({})
        VarLoader().parse_variables('${foo:-2:2}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

    def test_slice_by_variable_start(self):
        var = VarLoader().parse_variables('${foo:${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:${tmp}}')

    def test_slice_by_variable_negstart(self):
        var = VarLoader().parse_variables('${foo:-${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:-${tmp}}')

    def test_slice_by_variable_length(self):
        var = VarLoader().parse_variables('${foo:1:${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:1:${tmp}}')

    def test_slice_by_variable_neglength(self):
        var = VarLoader().parse_variables('${foo:1:-${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:1:-${tmp}}')

    def test_slice_by_two_variables(self):
        var = VarLoader().parse_variables('${foo:${x}:-${y}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:${x}:-${y}}')

    def test_slice_by_expression(self):
        var = VarLoader().parse_variables('${foo:$[1+1]:$[2+2]}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:$[1+1]:$[2+2]}')

    def test_sliced_function(self):
        var = VarLoader().parse_variables(
            '${CALLERID(num):0:-6}xxxxxx', DUMMY_WHERE)
        self.assertEqual(str(var), '${CALLERID(num):0:-6}xxxxxx')
