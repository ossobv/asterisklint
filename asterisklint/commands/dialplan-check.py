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
            'error classes through the ALINT_IGNORE environment variable.'))
    parser.add_argument(
        'dialplan', metavar='CONF',
        help="path to extensions.conf")
    args = parser.parse_args(args)

    parser = FileDialplanParser()
    parser.include(args.dialplan)
    dialplan = next(iter(parser))
    del dialplan

    if MessageDefManager.raised:
        return 1
