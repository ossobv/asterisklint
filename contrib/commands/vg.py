# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2017  Walter Doekes, OSSO B.V.
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
Monkey patch the FileReader to read VoIPGRID style config. Then invoke
the 'command' argument. For example: dialplan-check
"""
import argparse
import asterisklint
import asterisklint.mainutil
import asterisklint.file
import sys

from asterisklint.file import (
    W_WSH_BOL, W_WSH_EOL, AsteriskCommentReader, BinFileReader,
    EncodingReader, FileformatReader, NoCtrlReader)
from asterisklint.main import load_command
from asterisklint.mainutil import MainBase


class VoipgridCommentReader(object):
    """
    A modified version of the AsteriskCommentReader that does two things:

    - Unfold long lines. The VoIPGRID func_odbc.conf uses folded lines
      for more readable SQL. Folded lines start with at least one space.
    - Comment separator recognition by nesting. The semicolon designates
      a comment only if it is not nested inside parentheses, single or
      double quotes.

    The parsed config files are fed to the "static config" table where
    the context, data and comments are already split, so both config
    "improvements" are performed without messing with Asterisk itself.
    """
    @staticmethod
    def voipgrid_comment_split(data, where):
        """
        Recognise a semicolon as comment separator only if it is not
        nested inside parentheses or quotes.

        Splits the data into data and comments.

        NOTE: There is no way to explicitly escape the semicolon (or to
        escape the nesting tokens).
        """
        if not data:
            return '', ''

        arr = [0]
        for i, char in enumerate(data):
            if char == '"':
                if arr[-1] == '"':
                    arr.pop()
                else:
                    arr.append('"')
            elif char == "'":
                if arr[-1] == "'":
                    arr.pop()
                else:
                    arr.append("'")
            elif char == '(':
                if arr[-1] == '"':
                    pass
                else:
                    arr.append('(')
            elif char == ')':
                if arr[-1] == '"':
                    pass
                else:
                    if arr[-1] == '(':
                        arr.pop()
            elif char == ';':
                if len(arr) == 1:
                    i -= 1
                    break

        data, comment = data[0:i + 1], data[i + 1:]
        return AsteriskCommentReader._move_middle_space_to_comment(
            data, comment, where)

    def __iter__(self):
        prev = ()

        for where, data in super().__iter__():
            # If there was previous data and this is not a continuation,
            # then yield.
            if prev and not data.startswith(tuple(' \t')):
                yield prev
                prev = ()

            # We cannot escape whitespace, so no need to keep this
            # around.
            if data.endswith(tuple(' \t')):
                W_WSH_EOL(where)
                data = data.rstrip(' \t')

            # Split comment?
            data, comment = self.voipgrid_comment_split(data, where)

            # If prev is still set, this is a continuation/folded line.
            if prev:
                if not prev[1]:
                    # Empty line that gets a continuation? No good. That
                    # could mean that you're trying to line-fold a
                    # comment: "; foo\n bar" -- that doesn't make sense
                    W_WSH_BOL(where)

                # Keep initial where, append data and comment.
                prev = (prev[0], prev[1] + data, prev[2] + comment)

            # If this is an include, we shall yield immediately, lest we
            # break out of the iteration. Otherwise we'd ignore #includes
            # at the end of the file.
            elif data.startswith('#'):
                yield where, data, comment

            else:
                prev = where, data, comment

        if prev:
            yield prev


##############################
# Create a custom FileReader #
##############################

class VoipgridFileReader(
        VoipgridCommentReader, FileformatReader, NoCtrlReader,
        EncodingReader, BinFileReader):
    pass

asterisklint.file.FileReader = VoipgridFileReader


######################################################################
# Then proceed to monkey patch all the users with the new FileReader #
# and add a context-resetting method because new contexts in VG wipe #
# existing contexts instead of appending to them.                    #
######################################################################

class VoipgridFileConfigParser(
        asterisklint.ConfigAggregator, VoipgridFileReader):

    def on_context(self, context):
        # Wipe any previous contexts with the same name.
        try:
            self._contexts.remove(context)
        except ValueError:
            pass

        return super().on_context(context)

asterisklint.FileConfigParser = VoipgridFileConfigParser


class VoipgridFileDialplanParser(
        asterisklint.DialplanAggregator, VoipgridFileReader):

    def on_context(self, context):
        # Wipe any previous contexts with the same name.
        if context.name == 'general' and self._dialplan._general:
            assert False, '[general] overridden?'
            self._dialplan._general = None
        elif context.name == 'globals' and self._dialplan._globals:
            assert False, '[globals] overridden?'
            self._dialplan._globals = None
        elif context.name in self._prevcontexts:
            # Nasty. This is rather fragile, and doesn't even clean up
            # everything (like label references that were added).
            oldcontext = self._prevcontexts[context.name]
            del self._prevcontexts[context.name]
            self._dialplan.contexts.remove(oldcontext)
            del self._dialplan.contexts_by_name[context.name]

        return super().on_context(context)

asterisklint.FileDialplanParser = VoipgridFileDialplanParser


class VoipgridFileFuncOdbcParser(
        asterisklint.FuncOdbcAggregator, VoipgridFileReader):

    def on_context(self, context):
        # Wipe any previous contexts with the same name.
        try:
            self._contexts.remove(context)
        except ValueError:
            pass

        return super().on_context(context)

asterisklint.FileFuncOdbcParser = VoipgridFileFuncOdbcParser
asterisklint.mainutil.FileFuncOdbcParser = VoipgridFileFuncOdbcParser


#######################################################
# Create custom command that loads up another command #
#######################################################

class Main(MainBase):
    def create_argparser(self, argparser_class):
        parser = argparser_class(
            description=(
                'Monkey patch the FileReader to read VoIPGRID style config. '
                'Then call the next parameter as command, for example: '
                'dialplan-check'))
        parser.add_argument('command')
        parser.add_argument('args', nargs=argparse.REMAINDER)
        return parser

    def handle_args(self, args):
        try:
            command_module = load_command(args.command)
        except ImportError as exception:
            print('Cannot load command {!r}: {}'.format(
                args.command, exception), file=sys.stderr)
            return 1

        return command_module.main(args.args, envs={'FIXME': 'issue/18'})

main = Main()
