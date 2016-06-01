# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2016  Walter Doekes, OSSO B.V.
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
from asterisklint.app.vall.builtin import GotoIf
from asterisklint.varfun import VarLoader
from asterisklint.where import DUMMY_WHERE


class GotoIfArgsTest(ALintTestCase):
    def funcarg(self, arg):
        func = GotoIf()
        parsed = VarLoader().parse_variables(arg, DUMMY_WHERE)
        ignored = []
        func(parsed, jump_destinations=ignored, where=DUMMY_WHERE)

    def test_proper_goto(self):
        self.funcarg('$["${foo}"="1"]?new_context,${EXTEN},1')

    def test_too_few(self):
        self.funcarg('$["${foo}"="1"]')
        self.assertLinted({'E_APP_ARG_FEW': 1})

    def test_too_many(self):
        self.funcarg('$["${foo}"="1"]?iftrue:iffalse:ifother?excess-data')
        self.assertLinted({'E_APP_ARG_MANY': 1})

    def test_missing_question(self):
        self.funcarg('$["${foo}"="1"]new_context,${EXTEN},1')
        self.assertLinted({'E_APP_ARG_IFCONST': 1,
                           'E_APP_ARG_IFSTYLE': 1})

    def test_old_style_comma(self):
        self.funcarg('$["${foo}"="1"],new_context,${EXTEN},1')
        self.assertLinted({'E_APP_ARG_IFSTYLE': 1})

    def test_cond_var(self):
        self.funcarg('${var}?iftrue:iffalse')

    def test_cond_const_0(self):
        self.funcarg('0?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFCONST': 1})

    def test_cond_const_1(self):
        self.funcarg('1?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFCONST': 1})

    def test_cond_const_mid(self):
        self.funcarg('${var1}1${var2}?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFCONST': 1})

    def test_cond_const_mid_space(self):
        self.funcarg('${var1} ${var2}?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFCONST': 1})

    def test_cond_const_void(self):
        self.funcarg('?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFEMPTY': 1})

    def test_cond_const_only_space(self):
        self.funcarg('   ?iftrue:iffalse')
        self.assertLinted({'E_APP_ARG_IFEMPTY': 1})

    def test_cond_nonconst_space(self):
        """
        Allow spaces in the condition.
        """
        self.funcarg('   ${var}   ?iftrue:iffalse')
