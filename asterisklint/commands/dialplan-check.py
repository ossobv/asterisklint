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
        'dialplan', metavar='EXTENSIONS_CONF',
        help="path to extensions.conf")
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
    del dialplan

    # MessageDefManager.raised is a dict of messages ordered by message
    # type. All message types share the same muted flag, so we need only
    # examine the first.
    if any(not i[0].muted for i in MessageDefManager.raised.values()):
        return 1
