#!/usr/bin/env python3
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
"""
Show which variables are used by the dialplan.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asterisklint import FileDialplanParser
from asterisklint.varfun import VarLoader


loader = VarLoader()
parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))

print('Variables encountered:')
for variable, occurrences in sorted(
        loader._variables.items(), key=(lambda x: x[0].lower())):
    print('  {:20}  [{} times in {} files]'.format(
        variable, len(occurrences),
        len(set(i.filename for i in occurrences))))
