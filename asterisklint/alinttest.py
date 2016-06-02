# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2016  Walter Doekes, OSSO B.V.
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
from collections import defaultdict
from io import BytesIO
from unittest import (
    TestCase, TextTestResult, TextTestRunner, main as orig_main)

from .defines import MessageDefManager


__all__ = ('ALintTestCase', 'NamedBytesIO', 'ignoreLinted')


class ALintTestCase(TestCase):
    def setUp(self):
        MessageDefManager.muted = True  # could do this on runner startup..
        self.linted_counts = defaultdict(int)

    def tearDown(self):
        if self.last_test_was_a_success():
            self.assertLinted({})
        MessageDefManager.reset()

    def last_test_was_a_success(self):
        """
        Hope that unittest for Python3.4 doesn't change.
        """
        # If the test was "supposed to fail", we still want it reported
        # as a failure.
        if self._outcome.expectedFailure:
            return False

        # The error list holds accumulated status reports (not all of
        # them errors).
        last_error = self._outcome.errors[-1]
        test_method, errors = last_error
        return not bool(errors)

    def assertLinted(self, expected_counts):
        raised = MessageDefManager.raised
        counts = dict((id_, len(messages)) for id_, messages in raised.items())
        for id_, count in counts.items():
            self.linted_counts[id_] += count
        MessageDefManager.reset()

        # Strip messages that we're supposed to ignore. It can be tacked
        # onto the class or onto individual test methods.
        if hasattr(self, '__alinttest_ignore__'):
            # Use getattr instead of self.__alinttest_ignore__ because of
            # the mangled name.
            ignore = getattr(self, '__alinttest_ignore__')
        else:
            # Previously, we wrapped the ignorance into the test itself,
            # but then we'd forget to ignore the test during the
            # tearDown routine.
            curtest = getattr(self, self._testMethodName)
            ignore = getattr(curtest, '__alinttest_ignore__', False)

        # Something to ignore?
        if ignore:
            for key in list(counts.keys()):
                if ignore(key):
                    del counts[key]
                    # print('ignoring {} because of {}'.format(key, ignore))

        # Run this last, so we've completed the reset.
        self.assertEqual(counts, expected_counts)

    def create_instance_and_load_single_file(self, class_, filename, data):
        """
        A bit strange to have this here, but our main testing involves
        create an instance of SomeClass and loading up a sample data
        file.

        Example::

            filereader = self.create_instance_and_load_single_file(
                FileReader, 'test.conf', b'''data..''')
        """
        def opener(fn):
            assert fn == filename, (fn, filename)
            return NamedBytesIO(filename, data)
        instance = class_(opener=opener)
        instance.include(filename)
        return instance


class ALintTestResult(TextTestResult):
    def startTestRun(self):
        self.linted_counts = defaultdict(int)

    def stopTestRun(self):
        self.print_untested()

    def stopTest(self, test):
        if hasattr(test, 'linted_counts'):
            for id_, count in test.linted_counts.items():
                self.linted_counts[id_] += count
        elif (test.__class__.__name__ == 'ModuleImportFailure' or
              test.__class__.__name__ == '_FailedTest'):
            # Happens if we get module import errors during test load.
            # (ModuleImportFailure on python 3.4, _FailedTest on 3.5.)
            pass
        else:
            # Otherwise, this is probably a test, and that means that
            # you didn't call our setUp()...
            raise ValueError(
                'Did you forget to call super().setUp() on {!r}?'.format(
                    test.__class__.__name__))

        super().stopTest(test)

    def print_untested(self):
        tested = set(self.linted_counts.keys())
        defined = MessageDefManager.types
        untested = defined - tested

        if untested:
            print(
                ('\n\nStill untested messages:\n - {}'.format(
                 '\n - '.join(sorted(list(untested))))),
                file=self.stream)


class ALintTestRunner(TextTestRunner):
    def _makeResult(self):
        return ALintTestResult(self.stream, self.descriptions, self.verbosity)


class NamedBytesIO(BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name


class _IgnoreLinted(object):
    def __init__(self, *values):
        self._equals = []
        self._startswith = []

        for value in values:
            if not isinstance(value, str):
                raise TypeError('value {!r} is not a string'.format(value))

            parts = value.split('*')
            if len(parts) == 1:
                self._equals.append(parts[0])
            elif len(parts) == 2 and not parts[1]:
                self._startswith.append(parts[0])
            else:
                raise ValueError(
                    'only an optional trailing asterisk is valid in '
                    'value {!r}'.format(value))

        self._equals = tuple(self._equals)
        self._startswith = tuple(self._startswith)
        self._repr = 'ignoreLinted({})'.format(' '.join(values))

    def __call__(self, value):
        if value in self._equals or value.startswith(self._startswith):
            return True
        return False

    def __repr__(self):
        return self._repr


def ignoreLinted(*values):
    """
    Ignore linter hints/warnings/errors as supplied. Optionally, a
    trailing asterisk (*) may be used to match more.

    Example:

        @ignoreLinted('H_DP_*', 'W_SOME_WARNING')
        class MyTest(ALintTestCase):
            ...
    """
    def decorator(test_item):
        ignorefunc = _IgnoreLinted(*values)
        test_item.__alinttest_ignore__ = ignorefunc
        return test_item
    return decorator


def main():
    orig_main(
        module=None,  # now we can put 'discover' in the command line
        testRunner=ALintTestRunner)


if __name__ == '__main__':
    main()
