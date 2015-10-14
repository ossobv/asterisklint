#!/usr/bin/env python3
"""
WARNING: This script will write to your existing config!

It takes the E_APP_ARG_IFSTYLE messages, and rewrites your config,
changing the IF-syntax from the old comma-based form to the new
expected question-mark form.
"""
from collections import defaultdict, namedtuple
import sys

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager
from asterisklint.helper.mutator import FileMutatorBase
from asterisklint.app.base import E_APP_ARG_IFSTYLE


IfStyleError = namedtuple('IfStyleError', 'lineno app data cond args')


class Aggregator(object):
    def __init__(self):
        E_APP_ARG_IFSTYLE.add_callback(self.on_e_arg_ifstyle)
        self.issues_per_file = defaultdict(list)

    def on_e_arg_ifstyle(self, message):
        self.issues_per_file[message.where.filename].append(
            IfStyleError(
                lineno=(message.where.lineno - 1),  # 0-based
                app=message.fmtkwargs['app'],
                data=message.fmtkwargs['data'],
                cond=message.fmtkwargs['cond'],
                args=message.fmtkwargs['args']))


class ConvertDp104To1100Mutator(FileMutatorBase):
    def process_issue(self, issue, inline, outfile):
        if issue.app == 'ExecIf':
            assert issue.args, issue
            app_with_args = '{}({})'.format(
                issue.args[0], ','.join(str(i) for i in issue.args[1:]))

            # BUG: issue.data is not the original raw data, but already
            # parsed data, so it may not stringify back into the
            # original...
            needle = str(issue.data).encode('utf-8')
            replacement = '{}?{}'.format(issue.cond, app_with_args)
            replacement = replacement.encode('utf-8')

            outline = inline.replace(needle, replacement, 1)
            if inline == outline:
                raise AssertionError(
                    "We did not replace anything in {!r} "
                    "for issue {!r} and data '{}'".format(
                        inline, issue, issue.data))

            outfile.write(outline)
        else:
            raise NotImplementedError(issue)


MessageDefManager.muted = True  # no messages to stderr
aggregator = Aggregator()
parser = FileDialplanParser()
parser.include(sys.argv[1])

print('Converting dialplan from 1.4 to 11.')
print('Parsing current config...')
dialplan = next(iter(parser))
print()

mutator = ConvertDp104To1100Mutator(aggregator.issues_per_file)
mutator.request_permission_and_process()
