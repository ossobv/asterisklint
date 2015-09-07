# vim: set ts=8 sw=4 sts=4 et ai:
from collections import defaultdict
from io import BytesIO
from unittest import (
    TestCase, TextTestResult, TextTestRunner, main as orig_main)

from .defines import MessageDefManager


class ALintTestCase(TestCase):
    all_linted = defaultdict(int)  # global

    def setUp(self):
        MessageDefManager.muted = True  # could do this on runner startup..

    def tearDown(self):
        self.assertLinted({})  # also calls MessageDefManager.reset()

    def assertLinted(self, expected_counts):
        raised = MessageDefManager.raised
        counts = dict((id_, len(messages)) for id_, messages in raised.items())
        for id_, count in counts.items():
            ALintTestCase.all_linted[id_] += count

        self.assertEqual(counts, expected_counts)
        MessageDefManager.reset()


class ALintTestResult(TextTestResult):
    def stopTestRun(self):
        self.print_untested()

    def print_untested(self):
        tested = set(ALintTestCase.all_linted.keys())
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


def main():
    orig_main(
        module=None,  # now we can put 'discover' in the command line
        testRunner=ALintTestRunner)


if __name__ == '__main__':
    main()
