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
        'dialplan', metavar='EXTENSIONS_CONF',
        help="path to extensions.conf")
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
