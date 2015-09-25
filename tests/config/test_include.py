from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO, ignoreLinted
from asterisklint.config import Context, Varset


@ignoreLinted('W_WSH_*')  # temporarily ignore this
class NormalTest(ALintTestCase):
    def opener(self, filename):
        if filename == 'test.conf':
            return NamedBytesIO(filename, b'''\
[context1]
variable = value
#include "test2.conf"
variable2 = value2
''')
        elif filename == 'test2.conf':
            return NamedBytesIO(filename, b'''\
variable3 = value3
#include "test3.conf"
variable4 = value4
''')
        elif filename == 'test3.conf':
            return NamedBytesIO(filename, b'''\
variable5 = value5
[context2]
variable6 = value6
''')

    def test_normal(self):
        reader = FileConfigParser(opener=self.opener)
        reader.include('test.conf')

        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0].__class__, Context)
        self.assertEqual(out[0].name, 'context1')
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
