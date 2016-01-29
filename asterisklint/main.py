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
import argparse
import importlib
import os
import re
import sys

from . import alintver


# Don't allow leading underscores because then we'd find __init__ as
# well.
COMMAND_RE = re.compile(r'^[a-z0-9][a-z0-9_-]*$')


class NoSuchCommand(ValueError):
    pass


def wrap(text, skip, maxlen):
    lines = []
    words = text.split()
    maxlen -= (skip + 1)  # add one for the space
    for word in words:
        if not lines:
            lines.append(word)
        elif len(lines[-1]) + len(word) >= maxlen:
            lines.append(word)
        else:
            lines[-1] += ' ' + word
    return '\n{}'.format(' ' * skip).join(lines)


def list_commands(args, envs):
    """
    List the available commands by browsing through your pythonpath and
    listing the commands inside 'asterisklint.commands'.
    """
    commands_used = set()
    commands = []
    for path in sys.path:
        try:
            files = os.listdir(os.path.join(path, 'asterisklint', 'commands'))
        except OSError:
            pass
        else:
            for file_ in files:
                if file_.endswith('.py') and COMMAND_RE.match(file_[0:-3]):
                    command_name = file_[0:-3]
                    if command_name not in commands_used:
                        try:
                            command = load_command(command_name)
                        except NoSuchCommand as e:
                            command_desc = '(error: {})'.format(e)
                        else:
                            try:
                                command_desc = command.__doc__.strip()
                            except AttributeError:
                                command_desc = '(help text missing)'

                        commands_used.add(command_name)
                        commands.append((path, command_name, command_desc))
    commands.sort()

    fmt = '  {name:21} {desc}'
    print('builtin:')
    print(fmt.format(name='ls', desc='List available commands.'))
    last_path = None
    for path, name, desc in commands:
        if last_path != path:
            print()
            print('{}:'.format(path))
            last_path = path
        print(fmt.format(name=name, desc=wrap(desc, 24, 80)))
    print()
    print('Place custom commands in ~/.asterisklint/asterisklint/commands.')


def load_command(command):
    """
    Load ``command`` from the asterisklint.command namespace and return it.

    The command could be placed anywhere in your pythonpath, as long as
    it's inside the asterisklint.commands package.
    """
    if not COMMAND_RE.match(command):
        raise NoSuchCommand('Invalid tokens in command {!r}'.format(command))

    try:
        command_module = importlib.import_module(
            'asterisklint.commands.{}'.format(command))
    except ImportError as exception:
        raise NoSuchCommand('Could not load {!r}: {}'.format(
            command, exception))

    try:
        command_module.main
    except AttributeError:
        raise NoSuchCommand('Command {!r} has no entrypoint'.format(command))

    return command_module


def main(args, envs):
    # Insert ~/.asterisklint into path if it exists. This path construct
    # will also allow you to override any part of the application; like
    # add/remove individual Asterisk apps or functions.
    userdir = '{}/.asterisklint'.format(envs.get('HOME', '/dev/null'))
    if os.path.exists(userdir) and userdir not in sys.path:
        sys.path.insert(0, userdir)

    # Fetch first argument: the command.
    non_options = [i for i in args if not i.startswith('-')]
    if non_options:
        command = non_options[0]
        args.remove(command)

        # Builtin commands.
        if command == 'ls':
            list_commands(args, envs)

        # Dynamically loaded commands.
        else:
            try:
                command_module = load_command(command)
            except NoSuchCommand as e:
                print(e, file=sys.stderr)
                return 1

            # Update argv[0] for the command argparse help.
            sys.argv[0] = '{} {}'.format(sys.argv[0], command)
            # Run command main.
            return command_module.main(args, envs)

    # If there was no command, pass it along to the arg parser.
    else:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Check Asterisk PBX configuration syntax.')
        parser.add_argument(
            '-V', '--version', action='version',
            version="asterisklint {0.version_str}\n\n{0.license_str}".format(
                alintver))
        parser.add_argument(
            'command', metavar='COMMAND',
            help=("the command to execute, 'ls' lists the available "
                  "commands"))

        args = parser.parse_args(args)  # will fail/exit, because .. no command
