# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2017  Walter Doekes, OSSO B.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from asterisklint.alinttest import (
    ALintTestCase, expectedFailure, ignoreLinted)
from asterisklint.defines import HintDef, WarningDef
from asterisklint.where import DUMMY_WHERE

"""
NOTE: We define our custom hints *inside* the test cases because they
auto-register themselves upon definition. If we import this file but
don't run the tests, our test run would end with a warning that we did
not test our custom messages.
"""


class AssertLintedTestCase(ALintTestCase):
    def test_nothing(self):
        self.assertLinted({})

    def test_single(self):
        class H_MY_HINT(HintDef):
            message = 'irrelevant'

        # Raise a hint.
        H_MY_HINT(DUMMY_WHERE)

        self.assertLinted({'H_MY_HINT': 1})

    def test_multiple(self):
        class H_MY_HINT2(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING2(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT2(DUMMY_WHERE)
        W_MY_WARNING2(DUMMY_WHERE)
        H_MY_HINT2(DUMMY_WHERE)

        self.assertLinted({'H_MY_HINT2': 2, 'W_MY_WARNING2': 1})

    @ignoreLinted('W_WHATEVER', 'H_*')
    def test_ignore_with_asterisk(self):
        class H_MY_HINT3(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING3(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT3(DUMMY_WHERE)
        W_MY_WARNING3(DUMMY_WHERE)
        H_MY_HINT3(DUMMY_WHERE)

        self.assertLinted({'W_MY_WARNING3': 1})

    @ignoreLinted('H_MY_HINT4', 'W_WHATEVER')
    def test_ignore_without_asterisk(self):
        class H_MY_HINT4(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING4(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT4(DUMMY_WHERE)
        W_MY_WARNING4(DUMMY_WHERE)
        H_MY_HINT4(DUMMY_WHERE)

        self.assertLinted({'W_MY_WARNING4': 1})

    @ignoreLinted('*')
    def test_ignore_without_call_to_assertLinted(self):
        class H_MY_HINT5(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING5(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT5(DUMMY_WHERE)
        W_MY_WARNING5(DUMMY_WHERE)
        H_MY_HINT5(DUMMY_WHERE)


@ignoreLinted('H_SOMETHING_DIFFERENT', 'W_MY_WARN*')
class IgnoreAssertLintedTestCase(ALintTestCase):
    def test_ignorelinted_on_class(self):
        class H_MY_HINT6(HintDef):
            message = 'irrelevant'

        class W_MY_WARNING6(WarningDef):
            message = 'irrelevant'

        # Raise 2 hints and a warning.
        H_MY_HINT6(DUMMY_WHERE)
        W_MY_WARNING6(DUMMY_WHERE)
        H_MY_HINT6(DUMMY_WHERE)

        self.assertLinted({'H_MY_HINT6': 2})


class AssertLintedIsCalledOnTearDown(ALintTestCase):
    def tearDown(self):
        self.assertRaises(AssertionError, super().tearDown)

    def test_assertlinted_on_teardown(self):
        class W_MY_WARNING7(WarningDef):
            message = 'irrelevant'

        # Raise a warning, but don't check it. We must now get an error
        # raised from the tearDown().
        W_MY_WARNING7(DUMMY_WHERE)


class AssertLintedIsNotCalledIfAlreadyErrored(ALintTestCase):
    def tearDown(self):
        try:
            super().tearDown()
        except AssertionError:
            self.assertFalse(True, 'tearDown should not cause trouble')

    @expectedFailure
    def test_no_assertlinted_on_teardown(self):
        class W_MY_WARNING8(WarningDef):
            message = 'irrelevant'

        # Raise a warning.
        W_MY_WARNING8(DUMMY_WHERE)
        # Raise an Assertion failure. Now we *don't* want any checks in
        # tearDown().
        self.assertTrue(False)
