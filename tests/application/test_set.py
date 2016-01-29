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


@ignoreLinted('H_DP_GENERAL_MISPLACED', 'H_DP_GLOBALS_MISPLACED')
class SetTest(ALintTestCase):
    def get_extension(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 1)
        return contexts[0][0]

    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[context]
exten => s,1,Set(variable=value)
''')
        exten = self.get_extension(reader)
        self.assertEqual(exten.app.name, 'Set')
        # FIXME: test variable == value stuff?

    def test_canonical_case(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[context]
; proper case for "set" app is "Set"
exten => s,1,set(variable=value)
''')
        exten = self.get_extension(reader)
        del exten
        self.assertLinted({'W_APP_BAD_CASE': 1})
        # FIXME: test that variable is placed onto a global list of variables
        # FIXME: test that the app_set.so is placed onto a global list of
        # used modules
