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
Show dialplan like Asterisk does with CLI command "dialplan show". Takes
'extensions.conf' as argument.
"""
import argparse

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            'Shows the dialplan like Asterisk does with the CLI command '
            '"dialplan show". Useful for testing whether asterisklint '
            'parser the input properly.'))
    parser.add_argument(
        'dialplan', metavar='EXTENSIONS_CONF', nargs='?',
        default='./extensions.conf',
        help='path to extensions.conf')
    parser.add_argument(
        '--reverse', action='store_true',
        help="some versions of Asterisk output the dialplan file in reverse")
    args = parser.parse_args(args)

    MessageDefManager.muted = True  # no messages to stderr
    parser = FileDialplanParser()
    parser.include(args.dialplan)
    dialplan = next(iter(parser))
    print(dialplan.format_as_dialplan_show(
        reverse=args.reverse))
