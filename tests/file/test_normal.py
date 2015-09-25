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
        self.assertEqual(out[0][0].last_line, False)
        self.assertEqual(out[0][1], '[context]')

        self.assertEqual(out[1][0].filename, 'test.conf')
        self.assertEqual(out[1][0].lineno, 2)
        self.assertEqual(out[1][0].line, b'variable=value\n')
        self.assertEqual(out[1][0].last_line, False)
        self.assertEqual(out[1][1], 'variable=value')

        self.assertEqual(out[5][0].lineno, 6)
        self.assertEqual(out[5][0].last_line, True)
        self.assertEqual(out[5][1], 'and_that_is=it')
