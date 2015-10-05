from asterisklint.alinttest import ALintTestCase
from asterisklint.defines import WarningDef
from asterisklint.where import DUMMY_WHERE


class MessageTestCase(ALintTestCase):
    def test_normal(self):
        class W_WARNING1(WarningDef):
            message = 'irrelevant'

        W_WARNING1(DUMMY_WHERE)
        self.assertLinted({'W_WARNING1': 1})

    def test_format_required(self):
        class W_WARNING2(WarningDef):
            message = '{message} with {format}'

        # Properly formatted.
        W_WARNING2(DUMMY_WHERE, format='cheese', message='sandwitch')

        # Missing formats.
        self.assertRaises(
            KeyError,
            W_WARNING2, DUMMY_WHERE, message='sandwitch')

        self.assertLinted({'W_WARNING2': 2})
