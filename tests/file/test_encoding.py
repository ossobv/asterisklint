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
