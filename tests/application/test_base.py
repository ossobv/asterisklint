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
from asterisklint.app.base import AppBase
from asterisklint.app.vall.app_voicemail import VoiceMail
from asterisklint.varfun import VarLoader
from asterisklint.where import DUMMY_WHERE


class AppBaseSeparateArgsTest(ALintTestCase):
    def test_abc_def_ghi(self):
        self.assertEqual(
            AppBase.separate_args('abc,def,ghi'),
            ['abc', 'def', 'ghi'])

    def test_quoted_abc(self):
        self.assertEqual(
            AppBase.separate_args('"abc"'),
            ['abc'])

    def test_quoted_abc_def(self):
        self.assertEqual(
            AppBase.separate_args('"abc",def'),
            ['abc', 'def'])

    def test_quoted_abc_def_ghi(self):
        self.assertEqual(
            AppBase.separate_args('abc,"def","ghi"'),
            ['abc', 'def', 'ghi'])

    def test_other_delimiter(self):
        self.assertEqual(
            AppBase.separate_args('a,b,c|"d,e,f"|"ghi"', '|'),
            ['a,b,c', 'd,e,f', 'ghi'])

    def test_respect_quotes(self):
        self.assertEqual(
            AppBase.separate_args('"a,b,c","d",e,f'),
            ['a,b,c', 'd', 'e', 'f'])

    def test_respect_quotes_raw(self):
        self.assertEqual(
            AppBase.separate_args(
                '"a,b,c","d",e,f', remove_quotes_backslashes=False),
            ['"a,b,c"', '"d"', 'e', 'f'])

    def test_respect_backslashes(self):
        self.assertEqual(
            AppBase.separate_args('"abc\\",\\"def"'),
            ['abc","def'])

    def test_respect_backslashes_raw(self):
        self.assertEqual(
            AppBase.separate_args(
                '"abc\\",\\"def"', remove_quotes_backslashes=False),
            ['"abc\\",\\"def"'])

    def test_respect_brackets(self):
        self.assertEqual(
            AppBase.separate_args('abc,def[g[h[i],j],kl],mno'),
            ['abc', 'def[g[h[i],j],kl]', 'mno'])

    def test_respect_parens(self):
        self.assertEqual(
            AppBase.separate_args('abc,def(g(h(i),j),kl),mno'),
            ['abc', 'def(g(h(i),j),kl)', 'mno'])

    def test_respect_no_negative_close(self):
        self.assertEqual(
            AppBase.separate_args('abc)))(((,))),def'),
            ['abc)))(((,)))', 'def'])

    def test_respect_brackets_parens(self):
        # TODO: crazy bracket/parens combinations, we should warn here..
        self.assertEqual(
            AppBase.separate_args('abc,def[g(h]i(,j],k)),l],m([),]n)o'),
            ['abc', 'def[g(h]i(,j],k))', 'l]', 'm([),]n)o'])


class AppBaseCallTest(ALintTestCase):
    def call_app(self, appclass, data):
        where = DUMMY_WHERE
        app = appclass()
        var = VarLoader().parse_variables(data, where)
        ignored = []
        app(var, jump_destinations=ignored, where=where)

    def test_abcdefghi(self):
        self.call_app(AppBase, 'abc,def,ghi')

    def test_variables(self):
        self.call_app(AppBase, '${abc},def,ghi')

    def test_voicemail(self):
        self.call_app(VoiceMail, '${abc},s')
