from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO, ignoreLinted


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
        self.assertEqual([i.name for i in out], ['context1', 'context2'])

        variables = [i for i in out[0]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test.conf', 2, 'variable', 'value'),
             ('test2.conf', 1, 'variable3', 'value3'),
             ('test3.conf', 1, 'variable5', 'value5')])

        variables = [i for i in out[1]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test3.conf', 4, 'variable6', 'value6'),
             ('test2.conf', 2, 'variable4', 'value4'),
             ('test.conf', 3, 'variable2', 'value2')])
