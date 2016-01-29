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
from asterisklint import FileDialplanParser
from asterisklint.alinttest import (
    ALintTestCase, NamedBytesIO, ignoreLinted)


@ignoreLinted('H_DP_GENERAL_MISPLACED', 'H_DP_GLOBALS_MISPLACED')
class NormalTest(ALintTestCase):
    def create_parser(self, filename, data):
        def opener(fn):
            assert fn == filename, (fn, filename)
            return NamedBytesIO(filename, data)
        parser = FileDialplanParser(opener=opener)
        parser.include(filename)
        return parser

    def check_values(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 4)

    def test_normal(self):
        reader = self.create_parser('test.conf', b'''\
[context]
exten => s,1,NoOp()
 same => n(label2),Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
''')
        self.check_values(reader)

    def test_normal_noop_needs_no_parens(self):
        reader = self.create_parser('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
''')
        self.check_values(reader)

    def test_missing_parens(self):
        reader = self.create_parser('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup
exten => h,1,DumpChan
''')
        self.check_values(reader)
        self.assertLinted({'W_APP_NEED_PARENS': 2})  # hangup and dumpchan

    def test_missing_horizontalws_before(self):
        reader = self.create_parser('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),  Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
''')
        self.check_values(reader)
        self.assertLinted({'W_APP_WSH': 1})  # horizontal whitespace

    def test_missing_horizontalws_after(self):
        reader = self.create_parser('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose (foo)
 same => n,Hangup()
exten => h,1,DumpChan()
''')
        self.check_values(reader)
        self.assertLinted({'E_APP_WSH': 1})  # horizontal whitespace
