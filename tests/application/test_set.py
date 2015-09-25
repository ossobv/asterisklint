from asterisklint import FileDialplanParser
from asterisklint.alinttest import (
    ALintTestCase, NamedBytesIO, ignoreLinted)


@ignoreLinted('H_DP_GENERAL_MISPLACED', 'H_DP_GLOBALS_MISPLACED')
class SetTest(ALintTestCase):
    def get_extension(self, reader):
        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]

        contexts = dialplan.contexts
        self.assertEqual(len(contexts), 1)
        self.assertEqual(len(contexts[0]), 1)
        return contexts[0][0]

    def test_normal(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
exten => s,1,Set(variable=value)
'''))
        exten = self.get_extension(reader)
        self.assertEqual(exten.app.name, 'Set')
        # FIXME: test variable == value stuff?

    def test_canonical_case(self):
        reader = FileDialplanParser(NamedBytesIO('test.conf', b'''\
[context]
; proper case for "set" app is "Set"
exten => s,1,set(variable=value)
'''))
        exten = self.get_extension(reader)
        del exten
        self.assertLinted({'W_APP_BAD_CASE': 1})
        # FIXME: test that variable is placed onto a global list of variables
        # FIXME: test that the app_set.so is placed onto a global list of
        # used modules
