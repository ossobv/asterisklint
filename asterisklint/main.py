import argparse
import importlib
import os
import re
import sys


COMMAND_RE = re.compile(r'^[a-z0-9][a-z0-9_]*$')


class NoSuchCommand(ValueError):
    pass


def list_commands(args, envs):
    """
    List the available commands by browsing through your pythonpath and
    listing the commands inside 'asterisklint.commands'.
    """
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
                    try:
                        command = load_command(command_name)
                    except NoSuchCommand as e:
                        command_help = '(error: {})'.format(e)
                    else:
                        try:
                            command_help = command.help
                        except AttributeError:
                            command_help = '(help text missing)'
                    commands.append((command_name, command_help))
    commands.sort()

    fmt = '  {name:13} {help}'
    print('Builtins:')
    print(fmt.format(name='listcmd', help='List available commands.'))
    print()
    if commands:
        print('Dynamic:')
        for name, help in commands:
            print(fmt.format(name=name, help=help))
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
    except ImportError:
        raise NoSuchCommand('Command {!r} not found'.format(command))

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

    # Create arg parser and parse.
    parser = argparse.ArgumentParser(
        description='Check Asterisk PBX configuration syntax.')
    parser.add_argument(
        'command', metavar='CMD',
        help=('the command to execute, use the "listcmd" command'
              'to show the available commands'))

    args = parser.parse_args(args)

    # Builtin commands.
    if args.command == 'listcmd':
        list_commands(args, envs)

    # Dynamic commands.
    else:
        try:
            command = load_command(args.command)
        except NoSuchCommand as e:
            print(e)
            return 1

        command.main(args, envs)
