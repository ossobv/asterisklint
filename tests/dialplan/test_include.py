from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, ignoreLinted


class IncludeTest(ALintTestCase):
    maxDiff = 2048

    @ignoreLinted('*')  # don't care about formatting errors
    def test_random_include_order(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[context1]
include => context2
exten => _Z!,1,NoOp
 same => n,Goto(2${EXTEN:1})

[context2]
exten => _Z!,1,NoOp
 same => n,Set(CALLERID(num)=1234)
include => context1
 same => n,Dial(SIP/300)
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]
        fmt = dialplan.format_as_dialplan_show()

        self.assertEqual(fmt, '''\
[ Context 'context2' created by 'pbx_config' ]
  '_Z!' =>          1. NoOp()                                     [pbx_config]
                    2. Set(CALLERID(num)=1234)                    [pbx_config]
                    3. Dial(SIP/300)                              [pbx_config]
  Include =>        'context1'                                    [pbx_config]

[ Context 'context1' created by 'pbx_config' ]
  '_Z!' =>          1. NoOp()                                     [pbx_config]
                    2. Goto(2${EXTEN:1})                          [pbx_config]
  Include =>        'context2'                                    [pbx_config]
''')
