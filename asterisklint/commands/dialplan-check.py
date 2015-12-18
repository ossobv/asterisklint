"""
Do sanity checks on dialplan. Takes 'extensions.conf' as argument.
Suppress error classes using ALINT_IGNORE.
"""
import argparse

from asterisklint import FileDialplanParser
from asterisklint.defines import MessageDefManager


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            'Do sanity checks on dialplan. Suppress comma separated '
            'error classes through the ALINT_IGNORE environment variable. '
            'Returns 1 if any issue was reported.'))
    parser.add_argument(
        'dialplan', metavar='EXTENSIONS_CONF',
        help="path to extensions.conf")
    args = parser.parse_args(args)

    parser = FileDialplanParser()
    parser.include(args.dialplan)
    dialplan = next(iter(parser))
    del dialplan

    # MessageDefManager.raised is a dict of messages ordered by message
    # type. All message types share the same muted flag, so we need only
    # examine the first.
    if any(not i[0].muted for i in MessageDefManager.raised.values()):
        return 1
