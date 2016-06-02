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
Do sanity checks on dialplan. Takes 'extensions.conf' as argument.
Suppress error classes using ALINT_IGNORE.
"""
import argparse

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager
from asterisklint.mainutil import UniqueStore, load_func_odbc_functions


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            'Do sanity checks on dialplan. Suppress comma separated '
            'error classes through the ALINT_IGNORE environment variable. '
            'Returns 1 if any issue was reported.'))
    parser.add_argument(
        'dialplan', metavar='EXTENSIONS_CONF', nargs='?',
        default='./extensions.conf',
        help='path to extensions.conf')
    parser.add_argument(
        '--func-odbc', metavar='FUNC_ODBC_CONF', action=UniqueStore,
        help="path to func_odbc.conf, will be read automatically if found "
             "in same the same dir as extensions.conf; set empty to disable")
    args = parser.parse_args(args)

    # Load func_odbc functions if requested.
    load_func_odbc_functions(args.func_odbc, args.dialplan)

    parser = FileDialplanParser()
    parser.include(args.dialplan)
    dialplan = next(iter(parser))
    dialplan.walk_jump_destinations()
    del dialplan

    # MessageDefManager.raised is a dict of messages ordered by message
    # type. All message types share the same muted flag, so we need only
    # examine the first.
    if any(not i[0].muted for i in MessageDefManager.raised.values()):
        return 1
