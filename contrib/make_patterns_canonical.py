#!/usr/bin/env python3
"""
WARNING: This script will write to your existing config!

It takes the H_PAT_NON_CANONICAL messages, and rewrites your config,
changing the pattern from the current form to the expected form.
"""
from collections import defaultdict, namedtuple
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager
from asterisklint.helper.mutator import FileMutatorBase
from asterisklint.pattern import H_PAT_NON_CANONICAL


Replacement = namedtuple('Replacement', 'lineno needle replacement')


class Aggregator(object):
    def __init__(self):
        H_PAT_NON_CANONICAL.add_callback(self.on_message)
        self.issues_per_file = defaultdict(list)

    def on_message(self, message):
        self.issues_per_file[message.where.filename].append(
            Replacement(
                lineno=(message.where.lineno - 1),  # 0-based
                needle=message.fmtkwargs['pat'].encode('utf-8'),
                replacement=message.fmtkwargs['expected'].encode('utf-8')))


class MakePatternsCanonicalMutator(FileMutatorBase):
    def process_issue(self, issue, inline, outfile):
        # Split between "exten =>" and the rest.
        linehead, linetail = inline.split(b'=', 1)
        if linetail[0] == b'>':
            linehead += b'>'
            linetail = linetail[1:]

        # We can safely use replace-1 here. If we were able
        # to parse your config, we should not be looking
        # directly at a pattern first.
        linetail = linetail.replace(
            issue.needle, issue.replacement, 1)
        outline = linehead + b'=' + linetail

        # Write new line.
        outfile.write(outline)


MessageDefManager.muted = True  # no messages to stderr
aggregator = Aggregator()
parser = FileDialplanParser()
parser.include(sys.argv[1])

print('Making dialplan patterns into canonical form.')
print('Parsing current config...')
dialplan = next(iter(parser))
print()

mutator = MakePatternsCanonicalMutator(aggregator.issues_per_file)
mutator.request_permission_and_process()
