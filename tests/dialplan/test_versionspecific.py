from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, ignoreLinted


class VersionSpecificTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('H_*')
    def test_asterisk_1_4_has_lowercase_NZX_sort_bug(self):
        "Asterisk 1.4 has sort order issues with lowercase NZX."
        # This test does not reproduce the problem; it simply documents
        # that there was a problem in the past.
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[asterisk-1.4-sorting-bug]
exten => _X-0,1,NoOp(X)
exten => _x-1,1,NoOp(x)
exten => _N-0,1,NoOp(N)
exten => _n-1,1,NoOp(n)
exten => _Z-0,1,NoOp(Z)
exten => _z-1,1,NoOp(z)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        asterisk14_output = '''\
[ Context 'asterisk-1.4-sorting-bug' created by 'pbx_config' ]
  '_n-1' =>         1. NoOp(n)                                    [pbx_config]
  '_x-1' =>         1. NoOp(x)                                    [pbx_config]
  '_z-1' =>         1. NoOp(z)                                    [pbx_config]
  '_N-0' =>         1. NoOp(N)                                    [pbx_config]
  '_Z-0' =>         1. NoOp(Z)                                    [pbx_config]
  '_X-0' =>         1. NoOp(X)                                    [pbx_config]
'''
        asterisk_output = '''\
[ Context 'asterisk-1.4-sorting-bug' created by 'pbx_config' ]
  '_N-0' =>         1. NoOp(N)                                    [pbx_config]
  '_n-1' =>         1. NoOp(n)                                    [pbx_config]
  '_Z-0' =>         1. NoOp(Z)                                    [pbx_config]
  '_z-1' =>         1. NoOp(z)                                    [pbx_config]
  '_X-0' =>         1. NoOp(X)                                    [pbx_config]
  '_x-1' =>         1. NoOp(x)                                    [pbx_config]
'''
        self.assertEqual(fmt, asterisk_output)
        del asterisk14_output
