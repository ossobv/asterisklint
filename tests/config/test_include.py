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
#include "test3.conf"
variable3 = value3
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
             ('test3.conf', 1, 'variable5', 'value5')])

        variables = [i for i in out[1]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test3.conf', 4, 'variable6', 'value6'),
             ('test2.conf', 2, 'variable3', 'value3'),
             ('test2.conf', 3, 'variable4', 'value4'),
             ('test.conf', 4, 'variable2', 'value2')])


class LineNumberTest(ALintTestCase):
    """
    Initially, there was a bug, where the variable=value on line 3 would
    get marked as being on line 2. Test that that's fixed.
    """
    def opener(self, filename):
        if filename == 'test.conf':
            return NamedBytesIO(filename, b'''\
[context1]
#include "test2.conf"
variable=value  ; line 3
''')
        elif filename == 'test2.conf':
            return NamedBytesIO(filename, b'''\
variable2=value2
''')

    def test_correct_linenumber(self):
        reader = FileConfigParser(opener=self.opener)
        reader.include('test.conf')

        out = [i for i in reader]
        self.assertEqual([i.name for i in out], ['context1'])

        variables = [i for i in out[0]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test2.conf', 1, 'variable2', 'value2'),
             ('test.conf', 3, 'variable', 'value')])


class WithBlanksTest(ALintTestCase):
    def opener(self, filename):
        if filename == 'test.conf':
            return NamedBytesIO(filename, b'''\
  [context1]
 variable=value
   #include\x01\x02"test2.conf"
variable2=value2  ; line 4 (and not line 3, keep this test!)
''')
        elif filename == 'test2.conf':
            return NamedBytesIO(filename, b'''\
  variable3 = value3
  ; this is line 2
 variable4 = value4
''')

    def test_with_leading_blanks(self):
        reader = FileConfigParser(opener=self.opener)
        reader.include('test.conf')

        out = [i for i in reader]
        self.assertEqual([i.name for i in out], ['context1'])

        variables = [i for i in out[0]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test.conf', 2, 'variable', 'value'),
             ('test2.conf', 1, 'variable3', 'value3'),
             ('test2.conf', 3, 'variable4', 'value4'),
             ('test.conf', 4, 'variable2', 'value2')])

        self.assertLinted({'W_FILE_CTRL_CHAR': 1, 'W_WSH_BOL': 5,
                           'W_WSH_CTRL': 1, 'W_WSH_VARSET': 2})


class WhiteSpaceInIncludesTest(ALintTestCase):
    def opener(self, filename):
        if filename == 'test.conf':
            return NamedBytesIO(filename, b'''\


[context1]
variable=value
#include "test2.conf"

[context3]
variable3=value3


''')
        elif filename == 'test2.conf':
            return NamedBytesIO(filename, b'''\


[context2]
variable2=value2


''')

    @ignoreLinted('H_WSV_CTX_BETWEEN')  # don't care about this now
    def test_with_two_bof_eof_warnings(self):
        reader = FileConfigParser(opener=self.opener)
        reader.include('test.conf')

        out = [i for i in reader]
        self.assertEqual([i.name for i in out],
                         ['context1', 'context2', 'context3'])

        variables = [i for i in out[0]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test.conf', 4, 'variable', 'value')])
        variables = [i for i in out[1]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test2.conf', 4, 'variable2', 'value2')])
        variables = [i for i in out[2]]
        self.assertEqual(
            [(i.where.filename, i.where.lineno, i.variable, i.value)
             for i in variables],
            [('test.conf', 8, 'variable3', 'value3')])

        self.assertLinted({'W_WSV_BOF': 2, 'W_WSV_EOF': 2})
