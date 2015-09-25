from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase


class NormalTest(ALintTestCase):
    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[general]
writeprotect=yes

[globals]
GLOBAL1=X
GLOBAL2=Y

[non_empty_context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup()

[empty_context]
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 2)
        self.assertEqual(len(contexts[0]), 3)
        self.assertEqual(len(contexts[1]), 0)
