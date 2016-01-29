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


class EncodingTest(ALintTestCase):
    def test_utf8(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'utf8.conf', b'''\
[c\xc3\xb6ntext]
variable=value
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0][1], '[c\u00f6ntext]')

    def test_cp1252(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'cp1252.conf', b'''\
[cont\x80xt]
variable=value
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0][1], '[cont\u20acxt]')
        self.assertLinted({'E_FILE_UTF8_BAD': 1})

    def test_utf8_and_cp1252(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'encodingmess.conf', b'''\
[c\xc3\xb6nt\x80xt]
variable=value
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0][1], '[c\u00c3\u00b6nt\u20acxt]')
        self.assertLinted({'E_FILE_UTF8_BAD': 1})
