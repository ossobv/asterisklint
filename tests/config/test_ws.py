from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO


class HorizontalWhitespaceTest(ALintTestCase):
    def check_values(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].name, 'context')

        variables = [i for i in out[0]]
        self.assertEqual(len(variables), 1)
        self.assertEqual(variables[0].variable, 'foo')
        self.assertEqual(variables[0].value, 'bar')

    def test_wsh_bol_1(self):
        "Leading white space before [context]."
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b' [context]\n'))
        self.assertEqual(len([i for i in reader]), 0)
        self.assertLinted({'E_CONF_BAD_LINE': 1})

    def test_wsh_bol_2(self):
        "Leading white space before variable."
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b'[context]\n  foo=bar\n'))
        self.check_values(reader)
        self.assertLinted({'W_WSH_BOL': 1})

    def test_wsh_bol_3(self):
        "Leading white with tabs space before variable."
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b'[context]\n\t foo=bar\n'))
        self.check_values(reader)
        self.assertLinted({'W_WSH_BOL': 1})

    def test_wsh_eol(self):
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b'[context] \nfoo=bar \n'))
        self.check_values(reader)
        self.assertLinted({'W_WSH_EOL': 2})

    def test_wsh_varset(self):
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b'[context]\nfoo = bar\n'))
        self.check_values(reader)
        self.assertLinted({'W_WSH_VARSET': 1})

    def test_wsh_objset(self):
        reader = FileConfigParser(NamedBytesIO(
            'test.conf', b'[context]\nfoo=>bar\n'))
        self.check_values(reader)
        self.assertLinted({'W_WSH_OBJSET': 1})
