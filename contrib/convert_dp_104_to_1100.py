#!/usr/bin/env python3
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
"""
WARNING: This script will write to your existing config!

It takes the E_APP_ARG_IFSTYLE messages, and rewrites your config,
changing the IF-syntax from the old comma-based form to the new
expected question-mark form.
"""
from collections import defaultdict, namedtuple
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
