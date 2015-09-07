from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO
from asterisklint.config import Context, Varset


class NormalTest(ALintTestCase):
    def test_normal(self):
        reader = FileConfigParser(NamedBytesIO('test.conf', b'''\
[context]
variable => value
other=value2

[context2]
and_that_is=it
'''))
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
