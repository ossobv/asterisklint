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


class VersionSpecificTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('H_*')
    def test_asterisk_1_4_has_lowercase_NZX_sort_bug(self):
        "Asterisk 1.4 has sort order issues with lowercase NZX."
        # This test does not reproduce the problem; it simply documents
        # that there was a problem in the past.
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[asterisk-1.4-sorting-bug]
exten => _X-0,1,NoOp(X)
exten => _x-1,1,NoOp(x)
exten => _N-0,1,NoOp(N)
exten => _n-1,1,NoOp(n)
exten => _Z-0,1,NoOp(Z)
exten => _z-1,1,NoOp(z)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        asterisk14_output = '''\
[ Context 'asterisk-1.4-sorting-bug' created by 'pbx_config' ]
  '_n-1' =>         1. NoOp(n)                                    [pbx_config]
  '_x-1' =>         1. NoOp(x)                                    [pbx_config]
  '_z-1' =>         1. NoOp(z)                                    [pbx_config]
  '_N-0' =>         1. NoOp(N)                                    [pbx_config]
  '_Z-0' =>         1. NoOp(Z)                                    [pbx_config]
  '_X-0' =>         1. NoOp(X)                                    [pbx_config]
'''
        asterisk_output = '''\
[ Context 'asterisk-1.4-sorting-bug' created by 'pbx_config' ]
  '_N-0' =>         1. NoOp(N)                                    [pbx_config]
  '_n-1' =>         1. NoOp(n)                                    [pbx_config]
  '_Z-0' =>         1. NoOp(Z)                                    [pbx_config]
  '_z-1' =>         1. NoOp(z)                                    [pbx_config]
  '_X-0' =>         1. NoOp(X)                                    [pbx_config]
  '_x-1' =>         1. NoOp(x)                                    [pbx_config]
'''
        self.assertEqual(fmt, asterisk_output)
        del asterisk14_output
