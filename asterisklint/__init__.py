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
from .config import ConfigAggregator
from .dialplan import DialplanAggregator
from .file import FileReader
from .func_odbc import FuncOdbcAggregator


class FileConfigParser(ConfigAggregator, FileReader):
    pass


class FileDialplanParser(DialplanAggregator, FileReader):
    pass


class FileFuncOdbcParser(FuncOdbcAggregator, FileReader):
    pass
