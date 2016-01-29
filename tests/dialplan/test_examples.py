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


class ExamplesTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('H_*')
    def test_duplicate_prio_is_dropped(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[abc]
exten => s,1,NoOp(1)
exten => s,n,NoOp(2)
exten => h,1,NoOp(3)
exten => s,1,NoOp(another)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'E_DP_PRIO_DUPE': 1})  # duplicate s,1

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'abc' created by 'pbx_config' ]
  'h' =>            1. NoOp(3)                                    [pbx_config]
  's' =>            1. NoOp(1)                                    [pbx_config]
                    2. NoOp(2)                                    [pbx_config]
''')

    @ignoreLinted('H_*')
    def test_leading_spaces_are_allowed(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
\t [abc]
exten => s,1,NoOp(1)
   exten => s,n,NoOp(2)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'W_WSH_BOL': 2})

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'abc' created by 'pbx_config' ]
  's' =>            1. NoOp(1)                                    [pbx_config]
                    2. NoOp(2)                                    [pbx_config]
''')

    @ignoreLinted('H_*')
    def test_contexts_can_be_appended_to(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[context1]
exten => 100,1,NoOp(100)
exten => 101,1,NoOp(101)

[context2]
exten => 200,1,NoOp(200)
exten => 201,1,NoOp(201)

[context1]
exten => 100,1,NoOp("dupe, won't work")
exten => 102,1,NoOp(102)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'E_DP_PRIO_DUPE': 1})

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'context2' created by 'pbx_config' ]
  '200' =>          1. NoOp(200)                                  [pbx_config]
  '201' =>          1. NoOp(201)                                  [pbx_config]

[ Context 'context1' created by 'pbx_config' ]
  '100' =>          1. NoOp(100)                                  [pbx_config]
  '101' =>          1. NoOp(101)                                  [pbx_config]
  '102' =>          1. NoOp(102)                                  [pbx_config]
''')

    @ignoreLinted('H_*')
    def test_new_context_does_not_reset_n(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[quirk1]
exten => s,1,NoOp(1)
exten => s,n,NoOp(2)
exten => s,n,NoOp(3)

[quirk2]
exten => t,1,NoOp(t1)
exten => t,n,NoOp(t2)

[quirk1]
exten => s,n,NoOp(4) ; E_DP_PRIO_DUPE: tries to overwrite s3
exten => s,n,NoOp(5) ; W_DP_PRIO_BADORDER: context_last_prio should be reset

[quirk3]
exten => h,n,NoOp(h) ; W_DP_PRIO_BADORDER: it works, but order is stupid
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'E_DP_PRIO_DUPE': 1, 'W_DP_PRIO_BADORDER': 2})

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'quirk3' created by 'pbx_config' ]
  'h' =>            5. NoOp(h)                                    [pbx_config]

[ Context 'quirk2' created by 'pbx_config' ]
  't' =>            1. NoOp(t1)                                   [pbx_config]
                    2. NoOp(t2)                                   [pbx_config]

[ Context 'quirk1' created by 'pbx_config' ]
  's' =>            1. NoOp(1)                                    [pbx_config]
                    2. NoOp(2)                                    [pbx_config]
                    3. NoOp(3)                                    [pbx_config]
                    4. NoOp(5)                                    [pbx_config]
''')
