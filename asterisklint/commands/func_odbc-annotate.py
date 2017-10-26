# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2017  Walter Doekes, OSSO B.V.
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
Expand func_odbc.conf into wrapped/readable/annotated form. Takes
'func_odbc.conf' as argument.
"""
from asterisklint import FileFuncOdbcParser
from asterisklint.defines import MessageDefManager
from asterisklint.mainutil import MainBase


class Main(MainBase):
    def create_argparser(self, argparser_class):
        parser = argparser_class(
            description=(
                'Write the func_odbc SQL statements in a '
                'wrapped/readable/annotated form. In the future we may '
                'add a func_odbc-collapse to collapse the annotated form '
                'again.'))  # so we want output resembling func_odbc.conf
        parser.add_argument(
            'func_odbc', metavar='FUNC_ODBC_CONF', nargs='?',
            default='./func_odbc.conf',
            help="path to func_odbc.conf")
        return parser

    def handle_args(self, args):
        # No messages to stderr.
        MessageDefManager.muted = True

        parser = FileFuncOdbcParser()
        parser.include(args.func_odbc)
        print('-- BEWARE: This output format is not standardized yet')
        print('-- NOT FOR MACHINE CONSUMPTION')
        print('')

        for func_odbc_context in parser:
            print('-- {}'.format(func_odbc_context.get_function_name()))
            print('-- .')
            for key, query in sorted(func_odbc_context.get_queries().items()):
                print('-- FUNCTION TYPE: {}'.format(key))
                if key == 'read':
                    columns = query.select_columns()
                    if columns:
                        print('-- COLUMNS:')
                        for idx, column in enumerate(columns):
                            print('-- {:2d}. {}'.format(idx + 1, column))
                formatted = query.format_sql()
                if not formatted.endswith(';'):
                    formatted += ';'
                print(formatted)
            print()

main = Main()
