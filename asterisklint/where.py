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


class Where(object):
    def __init__(self, filename, lineno, line):
        self.filename = filename  # shared constant in CPython, so cheap
        self.lineno = lineno
        self.line = line

    def __str__(self):
        return '%s:%d' % (self.filename, self.lineno)


DUMMY_WHERE = Where(filename='<dummy>', lineno=-1, line='<dummy config line>')
