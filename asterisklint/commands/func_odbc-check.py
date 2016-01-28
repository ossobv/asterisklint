"""
Do sanity checks on func_odbc.conf. Takes 'func_odbc.conf' as argument.
Suppress error classes using ALINT_IGNORE.
"""
import argparse

from asterisklint import FileFuncOdbcParser
from asterisklint.defines import MessageDefManager


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            'Do sanity checks on dialplan. Suppress comma separated '
            'error classes through the ALINT_IGNORE environment variable. '
            'Returns 1 if any issue was reported.'))
    parser.add_argument(
        'func_odbc', metavar='FUNC_ODBC_CONF',
        help="path to func_odbc.conf")
    args = parser.parse_args(args)

    parser = FileFuncOdbcParser()
    parser.include(args.func_odbc)
    for func_odbc_context in parser:
        pass

    # MessageDefManager.raised is a dict of messages ordered by message
    # type. All message types share the same muted flag, so we need only
    # examine the first.
    if any(not i[0].muted for i in MessageDefManager.raised.values()):
        return 1
