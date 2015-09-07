from unittest import expectedFailure

from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase, NamedBytesIO


class SamePrioTest(ALintTestCase):
    def check_values(self, reader):
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.general), 0)
        self.assertEqual(len(dialplan.globals), 0)
        self.assertEqual(len(dialplan.contexts), 1)

        context = dialplan.contexts[0]
        self.assertEqual(len(context), 3)
        self.assertEqual(set(i.pattern for i in context), set(['pattern']))
        self.assertEqual([i.prio for i in context], [1, 2, 3])
        self.assertEqual([i.app for i in context],
                         ['NoOp({})'.format(i) for i in range(1, 4)])

    def test_exten_num_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,1,NoOp(1)
exten => pattern,2,NoOp(2)
exten => pattern,3,NoOp(3)
'''))
        self.check_values(reader)

    def test_exten_n_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,1,NoOp(1)
exten => pattern,n,NoOp(2)
exten => pattern,n,NoOp(3)
'''))
        self.check_values(reader)

    def test_same_n_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,1,NoOp(1)
 same => n,NoOp(2)
 same => n,NoOp(3)
'''))
        self.check_values(reader)


class BadPrioTest(ALintTestCase):
    def test_invalid_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,0,NoOp(1)
'''))
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.contexts[0]), 0)
        self.assertLinted({'E_DP_PRIO_INVALID': 1})

    def test_dupe_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,1,NoOp(1)
exten => pattern,2,NoOp(2)
exten => pattern,2,NoOp(3)
'''))
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.contexts[0]), 2)
        self.assertLinted({'E_DP_PRIO_DUPE': 1})

    def test_missing_prio_1(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,n,NoOp(1)
exten => pattern,n,NoOp(2)
exten => pattern,n,NoOp(3)
'''))
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.contexts[0]), 0)
        self.assertLinted({'E_DP_PRIO_MISSING': 3})

    def test_prio_bad_start(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => pattern,2,NoOp(1)
exten => pattern,n,NoOp(2)
exten => pattern,n,NoOp(3)
'''))
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.contexts[0]), 3)
        self.assertLinted({'W_DP_PRIO_BADORDER': 1})


class UnusualButGoodPrioTest(ALintTestCase):
    @expectedFailure
    def test_valid_prio(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => _X!,1,NoOp(1)
exten => _[0-3]!,2,NoOp(2)
exten => _[4-9]!,2,NoOp(2)
exten => _X!,3,NoOp(3)
'''))
        dialplan = [i for i in reader][0]
        self.assertEqual(len(dialplan.contexts[0]), 4)
        self.assertLinted({})  # NOT: {'W_DP_PRIO_BADORDER': 3}
