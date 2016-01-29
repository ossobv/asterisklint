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
import os

from . import FileFuncOdbcParser


class UniqueStore(argparse.Action):
    "Make sure an --argument is only used at most once."
    def __call__(self, parser, namespace, values, option_string):
        if getattr(namespace, self.dest, self.default) is not None:
            parser.error("{} appears several times".format(option_string))
        setattr(namespace, self.dest, values)


def load_func_odbc_functions(func_odbc_arg, dialplan_arg):
    if func_odbc_arg == '':
        # Explicit disable.
        return

    if func_odbc_arg is None:
        # Auto-detect?
        func_odbc_arg = os.path.join(
            os.path.dirname(dialplan_arg), 'func_odbc.conf')
        if not os.path.exists(func_odbc_arg):
            # If there is no such file, don't worry about it.
            return

    # Load it up.
    # TODO: do we want to silence func_odbc errors/warnings here?
    parser = FileFuncOdbcParser()
    parser.include(func_odbc_arg)
    for func_odbc_context in parser:
        pass
