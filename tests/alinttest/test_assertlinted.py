from asterisklint.alinttest import ALintTestCase, ignoreLinted
from asterisklint.defines import HintDef, WarningDef
from asterisklint.where import Where

"""
NOTE: We define our custom hints *inside* the test cases because they
auto-register themselves upon definition. If we import this file but
don't run the tests, our test run would end with a warning that we did
not test our custom messages.
"""


class DummyWhere(Where):
    def __init__(self):
        super().__init__(filename='dummy', lineno=-1, line='irrelevant')


class AssertLintedTestCase(ALintTestCase):
    def test_nothing(self):
        self.assertLinted({})

    def test_single(self):
        class H_MY_HINT(HintDef):
            message = 'irrelevant'

        # Raise a hint.
        H_MY_HINT(DummyWhere())

        self.assertLinted({'H_MY_HINT': 1})

    def test_multiple(self):
        class H_MY_HINT2(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING2(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT2(DummyWhere())
        W_MY_WARNING2(DummyWhere())
        H_MY_HINT2(DummyWhere())

        self.assertLinted({'H_MY_HINT2': 2, 'W_MY_WARNING2': 1})

    @ignoreLinted('W_WHATEVER', 'H_*')
    def test_ignore_with_asterisk(self):
        class H_MY_HINT3(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING3(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT3(DummyWhere())
        W_MY_WARNING3(DummyWhere())
        H_MY_HINT3(DummyWhere())

        self.assertLinted({'W_MY_WARNING3': 1})

    @ignoreLinted('H_MY_HINT4', 'W_WHATEVER')
    def test_ignore_without_asterisk(self):
        class H_MY_HINT4(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING4(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT4(DummyWhere())
        W_MY_WARNING4(DummyWhere())
        H_MY_HINT4(DummyWhere())

        self.assertLinted({'W_MY_WARNING4': 1})

    @ignoreLinted('*')
    def test_ignore_without_call_to_assertLinted(self):
        class H_MY_HINT5(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING5(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT5(DummyWhere())
        W_MY_WARNING5(DummyWhere())
        H_MY_HINT5(DummyWhere())


@ignoreLinted('H_SOMETHING_DIFFERENT', 'W_MY_WARN*')
class IgnoreAssertLintedTestCase(ALintTestCase):
    def test_ignorelinted_on_class(self):
        class H_MY_HINT6(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING6(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT6(DummyWhere())
        W_MY_WARNING6(DummyWhere())
        H_MY_HINT6(DummyWhere())

        self.assertLinted({'H_MY_HINT6': 2})
