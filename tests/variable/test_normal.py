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


class NormalTest(ALintTestCase):
    def test_var_foo(self):
        var = VarLoader().parse_variables('${foo}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo'))
        self.assertEqual(
            str(var), '${foo}')
        self.assertEqual(
            var.format(foo='ABC'), 'ABC')

    def test_var_foo_bar(self):
        var = VarLoader().parse_variables('${foo}${bar}', DUMMY_WHERE)
        self.assertEqual(
            var, Var.join([Var('foo'), Var('bar')]))
        self.assertEqual(
            str(var), '${foo}${bar}')
        self.assertEqual(
            var.format(foo='ABC', **{'bar': 'DEF'}), 'ABCDEF')

    def test_var_foo_bar_with_otherdata(self):
        var = VarLoader().parse_variables('//${foo}[$]${bar}$$', DUMMY_WHERE)
        self.assertEqual(
            var, Var.join(['//', Var('foo'), '[$]', Var('bar'), '$$']))
        self.assertEqual(
            str(var), '//${foo}[$]${bar}$$')
        self.assertEqual(
            var.format(foo='ABC', bar='DEF'), '//ABC[$]DEF$$')

    def test_simple_var_in_var(self):
        var = VarLoader().parse_variables('${${foo}}', DUMMY_WHERE)
        self.assertEqual(
            var, Var(Var('foo')))
        self.assertEqual(
            str(var), '${${foo}}')
        self.assertEqual(
            var.format(foo='bar', bar='DEF'), 'DEF')

    def test_joined_var_in_var(self):
        var = VarLoader().parse_variables('${${a}a${c}}', DUMMY_WHERE)
        self.assertEqual(
            var, Var(Var.join([Var('a'), 'a', Var('c')])))
        self.assertEqual(
            str(var), '${${a}a${c}}')
        self.assertEqual(
            var.format(a='b', c='r', bar='DEF'), 'DEF')
