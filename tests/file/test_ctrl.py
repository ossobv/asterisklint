from asterisklint.alinttest import ALintTestCase
from asterisklint.file import FileReader


class CtrlTest(ALintTestCase):
    def test_ctrl(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf', b'''\
[context]\x00
variable=value\v
other=value
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 3)
        self.assertLinted({'W_FILE_CTRL_CHAR': 2})
