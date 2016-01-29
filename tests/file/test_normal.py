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
from asterisklint.file import FileReader


class NormalTest(ALintTestCase):
    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf', b'''\
[context]
variable=value
other=value

[context2]
and_that_is=it
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 6)

        self.assertEqual(out[0][0].filename, 'test.conf')
        self.assertEqual(out[0][0].lineno, 1)
        self.assertEqual(out[0][0].line, b'[context]\n')
        self.assertEqual(out[0][1], '[context]')

        self.assertEqual(out[1][0].filename, 'test.conf')
        self.assertEqual(out[1][0].lineno, 2)
        self.assertEqual(out[1][0].line, b'variable=value\n')
        self.assertEqual(out[1][1], 'variable=value')

        self.assertEqual(out[5][0].lineno, 6)
        self.assertEqual(out[5][1], 'and_that_is=it')
