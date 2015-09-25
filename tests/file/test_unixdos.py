from asterisklint.alinttest import ALintTestCase
from asterisklint.file import FileReader


class UnixDosTest(ALintTestCase):
    def check_values(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0][1], '[context]')
        self.assertEqual(out[1][1], 'variable=value')
        self.assertEqual(out[2][1], 'other=value')

    def test_dos_with_bare_lf_1(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf',
            b'[context]\r\nvariable=value\nother=value')
        self.check_values(reader)
        self.assertLinted({'W_FILE_DOS_BARELF': 1})

    def test_dos_with_bare_lf_2(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf',
            b'[context]\r\nvariable=value\r\nother=value\n')
        self.check_values(reader)
        # We get two warnings here: one for the LF and one for the fact
        # that we have an LF at EOF at all in a DOS-format file.
        self.assertLinted({'W_FILE_DOS_BARELF': 1, 'W_FILE_DOS_EOFCRLF': 1})

    def test_dos_with_crlf_at_eof(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf',
            b'[context]\r\nvariable=value\r\nother=value\r\n')
        self.check_values(reader)
        self.assertLinted({'W_FILE_DOS_EOFCRLF': 1})

    def test_unix_without_lf(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf',
            b'[context]\nvariable=value\nother=value')
        self.check_values(reader)
        self.assertLinted({'W_FILE_UNIX_NOLF': 1})

    def test_unix_with_crlf(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf',
            b'[context]\nvariable=value\r\nother=value\n')
        self.check_values(reader)
        self.assertLinted({'W_FILE_UNIX_CRLF': 1})
