from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, ignoreLinted


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

    @ignoreLinted('H_*')
    def test_dupe_label(self):
        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', b'''\
[non_empty_context]
exten => s,1(label1),Verbose(foo1)
 same => n(label2),Verbose(foo2)
 same => n(label1),Verbose(foo3)
 same => n(label2),Verbose(foo4)
 same => n,Hangup()
''')
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 5)
        self.assertEqual(contexts[0][0].label, 'label1')
        self.assertEqual(contexts[0][1].label, 'label2')
        self.assertEqual(contexts[0][2].label, '')  # E_DP_LABEL_DUPE #1
        self.assertEqual(contexts[0][3].label, '')  # E_DP_LABEL_DUPE #2
        self.assertLinted({'E_DP_LABEL_DUPE': 2})
