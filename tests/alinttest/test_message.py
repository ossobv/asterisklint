from asterisklint.alinttest import ALintTestCase
from asterisklint.defines import WarningDef
from asterisklint.where import Where


class DummyWhere(Where):
    def __init__(self):
        super().__init__(filename='dummy', lineno=-1, line='irrelevant')


class MessageTestCase(ALintTestCase):
    def test_normal(self):
        class W_WARNING1(WarningDef):
            message = 'irrelevant'

        W_WARNING1(DummyWhere())
        self.assertLinted({'W_WARNING1': 1})

    def test_format_required(self):
        class W_WARNING2(WarningDef):
            message = '{message} with {format}'

        # Properly formatted.
        W_WARNING2(DummyWhere(), format='cheese', message='sandwitch')

        # Missing formats.
        self.assertRaises(
            KeyError,
            W_WARNING2, DummyWhere(), message='sandwitch')

        self.assertLinted({'W_WARNING2': 2})
