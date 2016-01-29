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
from asterisklint.alinttest import ALintTestCase, ignoreLinted


class NormalTest(ALintTestCase):
    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[general]
writeprotect=yes

[globals]
GLOBAL1=X
GLOBAL2=Y

[non_empty_context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup()

[empty_context]
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 2)
        self.assertEqual(len(contexts[0]), 3)
        self.assertEqual(len(contexts[1]), 0)

    @ignoreLinted('H_*')
    def test_dupe_label(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[non_empty_context]
exten => s,1(label1),Verbose(foo1)
 same => n(label2),Verbose(foo2)
 same => n(label1),Verbose(foo3)
 same => n(label2),Verbose(foo4)
 same => n,Hangup()
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 5)
        self.assertEqual(contexts[0][0].label, 'label1')
        self.assertEqual(contexts[0][1].label, 'label2')
        self.assertEqual(contexts[0][2].label, '')  # E_DP_LABEL_DUPE #1
        self.assertEqual(contexts[0][3].label, '')  # E_DP_LABEL_DUPE #2
        self.assertLinted({'E_DP_LABEL_DUPE': 2})
