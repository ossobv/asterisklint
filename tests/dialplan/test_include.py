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


class IncludeTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('*')  # don't care about formatting errors
    def test_random_include_order(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[context1]
include => context2
exten => _Z!,1,NoOp
 same => n,Goto(2${EXTEN:1})

[context2]
exten => _Z!,1,NoOp
 same => n,Set(CALLERID(num)=1234)
include => context1
 same => n,Dial(SIP/300)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        # Dialplan show defaults in reversed context order.. oddly
        # enough. But odbc-loaded data isn't? Because of the
        # cat_metrics?
        fmt = dialplan.format_as_dialplan_show()
        self.assertEqual(fmt, '''\
[ Context 'context2' created by 'pbx_config' ]
  '_Z!' =>          1. NoOp()                                     [pbx_config]
                    2. Set(CALLERID(num)=1234)                    [pbx_config]
                    3. Dial(SIP/300)                              [pbx_config]
  Include =>        'context1'                                    [pbx_config]

[ Context 'context1' created by 'pbx_config' ]
  '_Z!' =>          1. NoOp()                                     [pbx_config]
                    2. Goto(2${EXTEN:1})                          [pbx_config]
  Include =>        'context2'                                    [pbx_config]
''')
