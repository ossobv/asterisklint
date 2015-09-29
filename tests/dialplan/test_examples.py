from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, ignoreLinted


class ExamplesTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('H_*')
    def test_duplicate_prio_is_dropped(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[abc]
exten => s,1,NoOp(1)
exten => s,n,NoOp(2)
exten => h,1,NoOp(3)
exten => s,1,NoOp(another)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'E_DP_PRIO_DUPE': 1})  # duplicate s,1

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'abc' created by 'pbx_config' ]
  'h' =>            1. NoOp(3)                                    [pbx_config]
  's' =>            1. NoOp(1)                                    [pbx_config]
                    2. NoOp(2)                                    [pbx_config]
''')

    @ignoreLinted('H_*')
    def test_leading_spaces_are_allowed(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
\t [abc]
exten => s,1,NoOp(1)
   exten => s,n,NoOp(2)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        self.assertLinted({'W_WSH_BOL': 2})

        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'abc' created by 'pbx_config' ]
  's' =>            1. NoOp(1)                                    [pbx_config]
                    2. NoOp(2)                                    [pbx_config]
''')
