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
Report similarly named variables. Takes 'extensions.conf' as argument.
All parse errors are suppressed.
"""
import argparse

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager
from asterisklint.varfun import VarLoader

try:
    import editdistance  # https://pypi.python.org/pypi/editdistance
except ImportError:
    editdistance = None


def main(args, envs):
    # TODO: We'd like to report similarly named contexts and labels too.
    parser = argparse.ArgumentParser(
        description=(
            'Report similarly named variables. '
            'All parse errors are suppressed. Returns 1 if any potential '
            'issue was reported.'))
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='show a listing of variables encountered')
    parser.add_argument(
        'extensions', metavar='EXTENSIONS_CONF',
        help='path to extensions.conf')
    args = parser.parse_args(args)

    MessageDefManager.muted = True

    loader = VarLoader()
    parser = FileDialplanParser()
    parser.include(args.extensions)
    dialplan = next(iter(parser))
    del dialplan

    # TODO: loader._variables is *not* a public interface..
    varlist_by_name = list(sorted(
        loader._variables.items(), key=(lambda x: x[0].lower())))
    varlist_by_len = list(sorted(
        varlist_by_name, key=(lambda x: (len(x[0]), x[0].lower()))))

    if args.verbose:
        print('Variables encountered:')
        for variable, occurrences in varlist_by_name:
            print('  {:32}  [{} times in {} files]'.format(
                variable, len(occurrences),
                len(set(i.filename for i in occurrences))))
        print()

    # Levenshtein distance.
    if editdistance:
        similar = set()
        for list_of_variables in (varlist_by_name, varlist_by_len):
            prev = None
            for variable, occurrences in list_of_variables:
                if prev:
                    lodiff = editdistance.eval(prev.lower(), variable.lower())
                    if (lodiff == 0 and (
                                (prev.isupper() and variable.islower()) or
                                (prev.islower() and variable.isupper()))):
                        pass
                    elif (prev.startswith('ARG') and variable.startswith('ARG') and
                            prev[3:].isdigit() and variable[3:].isdigit()):
                        # ARG1..n as passed to a Gosub() routine.
                        pass
                    elif (lodiff <= 2 and lodiff < len(prev) and
                            lodiff < len(variable)):
                        similar.add(prev)
                        similar.add(variable)
                prev = variable

        if similar:
            print('Variables with similar names include:')
            for variable in sorted(similar, key=(lambda x: x.lower())):
                print('  {}'.format(variable))
            print()
            return 1

    elif not args.verbose:
        raise ImportError(
            'Loading editdistance failed. Using this command without '
            'the editdistance and without verbose mode is a no-op.')
