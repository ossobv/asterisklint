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
from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase
from asterisklint.config import Context, Varset


class NormalTest(ALintTestCase):
    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf', b'''\
[context]
variable => value
other=value2

[context2]
and_that_is=it
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0].__class__, Context)
        self.assertEqual(out[0].name, 'context')
        self.assertEqual(len(out[0]), 2)
        self.assertEqual(out[1].__class__, Context)
        self.assertEqual(out[1].name, 'context2')
        self.assertEqual(len(out[1]), 1)

        variables = [i for i in out[0]]
        self.assertEqual(variables[0].__class__, Varset)
        self.assertEqual(variables[0].variable, 'variable')
        self.assertEqual(variables[0].value, 'value')
        self.assertTrue(variables[0].arrow)

        self.assertEqual(variables[1].__class__, Varset)
        self.assertEqual(variables[1].variable, 'other')
        self.assertEqual(variables[1].value, 'value2')
        self.assertFalse(variables[1].arrow)

        variables = [i for i in out[1]]
        self.assertEqual([(i.variable, i.value) for i in variables],
                         [('and_that_is', 'it')])
