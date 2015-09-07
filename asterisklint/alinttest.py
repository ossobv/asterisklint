# vim: set ts=8 sw=4 sts=4 et ai:
from collections import defaultdict
from io import BytesIO
from unittest import (
    TestCase, TextTestResult, TextTestRunner, main as orig_main)

from .defines import MessageDefManager


class ALintTestCase(TestCase):
    def setUp(self):
        MessageDefManager.muted = True  # could do this on runner startup..
        self.linted_counts = defaultdict(int)

    def tearDown(self):
        self.assertLinted({})  # also calls MessageDefManager.reset()

    def assertLinted(self, expected_counts):
        raised = MessageDefManager.raised
        counts = dict((id_, len(messages)) for id_, messages in raised.items())
        for id_, count in counts.items():
            self.linted_counts[id_] += count
        MessageDefManager.reset()

        # Run this last, so we've completed the reset.
        self.assertEqual(counts, expected_counts)


class ALintTestResult(TextTestResult):
    def startTestRun(self):
        self.linted_counts = defaultdict(int)

    def stopTestRun(self):
        self.print_untested()

    def stopTest(self, test):
        if hasattr(test, 'linted_counts'):
            for id_, count in test.linted_counts.items():
                self.linted_counts[id_] += count
        else:
            # Happens if we get module import errors during test load.
            assert test.__class__.__name__ == 'ModuleImportFailure', \
                test.__class__.__mro__

        super(ALintTestResult, self).stopTest(test)

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
        super(NamedBytesIO, self).__init__(data)
        self.name = name


def main():
    orig_main(
        module=None,  # now we can put 'discover' in the command line
        testRunner=ALintTestRunner)


if __name__ == '__main__':
    main()
