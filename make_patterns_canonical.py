#!/usr/bin/env python3
"""
WARNING: This script will write to your existing config!

It takes the H_PAT_NON_CANONICAL messages, and rewrites your config,
changing the pattern from the current form to the expected form.
"""
from collections import defaultdict, namedtuple
from tempfile import NamedTemporaryFile
import os
import sys

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager
from asterisklint.pattern import H_PAT_NON_CANONICAL


Replacement = namedtuple('Replacement', 'lineno needle replacement')


class Aggregator(object):
    def __init__(self):
        H_PAT_NON_CANONICAL.add_callback(self.on_message)
        self.replacements_per_file = defaultdict(list)

    def on_message(self, message):
        self.replacements_per_file[message.where.filename].append(
            Replacement(
                lineno=(message.where.lineno - 1),  # 0-based
                needle=message.fmtkwargs['pat'].encode('utf-8'),
                replacement=message.fmtkwargs['expected'].encode('utf-8')))

MessageDefManager.muted = True  # no messages to stderr
aggregator = Aggregator()
parser = FileDialplanParser()
parser.include(sys.argv[1])

print('Parsing...')
dialplan = next(iter(parser))
print()

if not aggregator.replacements_per_file:
    print("Your dialplan does not throw H_PAT_NON_CANONICAL hints.")
    print("We're done here.")
    exit()

print('The following files have issues:')
filenames = list(sorted(aggregator.replacements_per_file.keys()))
print('  {}'.format('\n  '.join(filenames)))
yesno = input('Update all [y/n] ? ')
if yesno.strip() != 'y':
    print("You did not answer 'y'.")
    exit()

for filename in filenames:
    # Place the tempfile in the same dir, so renaming works (same
    # device).
    tempout = NamedTemporaryFile(
        dir=os.path.dirname(filename), mode='wb', delete=False)

    issues = aggregator.replacements_per_file[filename]
    try:
        issueptr = 0
        issue = issues[issueptr]
        with open(filename, 'rb') as file_:
            for lineno, line in enumerate(file_):
                if issue and lineno == issue.lineno:
                    # Split between "exten =>" and the rest.
                    linehead, linetail = line.split(b'=', 1)
                    if linetail[0] == b'>':
                        linehead += b'>'
                        linetail = linetail[1:]
                    # We can safely use replace-1 here. If we were able
                    # to parse your config, we should not be looking
                    # directly at a pattern first.
                    linetail = linetail.replace(
                        issue.needle, issue.replacement, 1)
                    line = linehead + b'=' + linetail
                    issueptr += 1
                    if issueptr < len(issues):
                        issue = issues[issueptr]
                    else:
                        issue = None
                tempout.write(line)
        tempout.flush()
    except:
        tempout.close()
        os.unlink(tempout.name)
        raise

    # Awesome, we've succeeded. Atomic move time!
    tempout.close()
    print('Overwriting', filename, '...')
    os.rename(tempout.name, filename)

print('Done')
