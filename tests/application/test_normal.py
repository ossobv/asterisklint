from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO


class NormalTest(ALintTestCase):
    def check_values(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 4)

    def test_normal(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,NoOp()
 same => n(label2),Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
'''))
        self.check_values(reader)
        self.assertLinted({'W_DP_GENERAL_MISPLACED': 1,
                           'W_DP_GLOBALS_MISPLACED': 1})

    def test_normal_noop_needs_no_parens(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
'''))
        self.check_values(reader)
        self.assertLinted({'W_DP_GENERAL_MISPLACED': 1,
                           'W_DP_GLOBALS_MISPLACED': 1})

    def test_missing_parens(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose(foo)
 same => n,Hangup
exten => h,1,DumpChan
'''))
        self.check_values(reader)
        self.assertLinted({'W_APP_NEED_PARENS': 2,  # hangup and dumpchan
                           'W_DP_GENERAL_MISPLACED': 1,
                           'W_DP_GLOBALS_MISPLACED': 1})

    def test_missing_horizontalws_before(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),  Verbose(foo)
 same => n,Hangup()
exten => h,1,DumpChan()
'''))
        self.check_values(reader)
        self.assertLinted({'W_APP_WSH': 1,  # horizontal whitespace
                           'W_DP_GENERAL_MISPLACED': 1,
                           'W_DP_GLOBALS_MISPLACED': 1})

    def test_missing_horizontalws_after(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,NoOp
 same => n(label2),Verbose (foo)
 same => n,Hangup()
exten => h,1,DumpChan()
'''))
        self.check_values(reader)
        self.assertLinted({'E_APP_WSH': 1,  # horizontal whitespace
                           'W_DP_GENERAL_MISPLACED': 1,
                           'W_DP_GLOBALS_MISPLACED': 1})
