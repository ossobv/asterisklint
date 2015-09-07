from asterisklint.alinttest import ALintTestCase, NamedBytesIO
from asterisklint.file import FileReader


class NormalTest(ALintTestCase):
    def test_ctrl(self):
        reader = FileReader(NamedBytesIO('test.conf', b'''\
[context]\x00
variable=value\v
other=value
'''))
        out = [i for i in reader]
        self.assertEqual(len(out), 3)
        self.assertLinted({'W_FILE_CTRL_CHAR': 2})
