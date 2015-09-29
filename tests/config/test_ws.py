from asterisklint import FileConfigParser
from asterisklint.alinttest import ALintTestCase


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
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b' [context]\n')
        self.assertEqual(len([i for i in reader]), 1)
        self.assertLinted({'W_WSH_BOL': 1})

    def test_wsh_bol_2(self):
        "Leading white space before variable."
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'[context]\n  foo=bar\n')
        self.check_values(reader)
        self.assertLinted({'W_WSH_BOL': 1})

    def test_wsh_bol_3(self):
        "Leading white with tabs space before variable."
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'[context]\n\t foo=bar\n')
        self.check_values(reader)
        self.assertLinted({'W_WSH_BOL': 1})

    def test_wsh_eol(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'[context] \nfoo=bar \n')
        self.check_values(reader)
        self.assertLinted({'W_WSH_EOL': 2})

    def test_wsh_varset(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'[context]\nfoo = bar\n')
        self.check_values(reader)
        self.assertLinted({'W_WSH_VARSET': 1})

    def test_wsh_objset(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'[context]\nfoo=>bar\n')
        self.check_values(reader)
        self.assertLinted({'W_WSH_OBJSET': 1})


class VerticalWhitespaceTest(ALintTestCase):
    def check_values(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0].name, 'context')
        self.assertEqual(out[1].name, 'context2')

        variables = [i for i in out[0]]
        self.assertEqual(len(variables), 2)
        self.assertEqual(variables[0].variable, 'foo')
        self.assertEqual(variables[0].value, 'bar')
        self.assertEqual(variables[1].variable, 'foo2')
        self.assertEqual(variables[1].value, 'bar2')

        variables = [i for i in out[1]]
        self.assertEqual(len(variables), 1)
        self.assertEqual(variables[0].variable, 'bar')
        self.assertEqual(variables[0].value, 'baz')

    def test_wsv_bof(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\

[context]
foo=bar
foo2=bar2

[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({'W_WSV_BOF': 1})

    def test_wsv_eof(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]
foo=bar
foo2=bar2

[context2]
bar=baz

''')
        self.check_values(reader)
        self.assertLinted({'W_WSV_EOF': 1})

    def test_wsv_bof_eof(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'\n\n\n')
        out = [i for i in reader]
        self.assertEqual(len(out), 0)
        self.assertLinted({'W_WSV_EOF': 1})

    def test_wsv_ctx_between_toofew(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]
foo=bar
foo2=bar2
[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({'H_WSV_CTX_BETWEEN': 1})

    def test_wsv_ctx_between_toomany(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]
foo=bar
foo2=bar2



[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({'H_WSV_CTX_BETWEEN': 1})

    def test_wsv_ctx_between_ok(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]
foo=bar
foo2=bar2


[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({})

    def test_wsv_ctx_between_okwithcomment(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]
foo=bar
foo2=bar2

;
;


[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({})

    def test_wsv_varset_between_ok(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]

foo=bar

foo2=bar2

[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({})

    def test_wsv_varset_between_okwithcomment(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]

foo=bar

; ok

foo2=bar2

[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({})

    def test_wsv_varset_between_notok(self):
        reader = self.create_instance_and_load_single_file(
            FileConfigParser, 'test.conf',
            b'''\
[context]


foo=bar


foo2=bar2

[context2]
bar=baz
''')
        self.check_values(reader)
        self.assertLinted({'H_WSV_VARSET_BETWEEN': 2})
