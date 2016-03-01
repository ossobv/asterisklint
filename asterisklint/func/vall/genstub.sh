#!/bin/sh
filename="$1"; shift
cat > $filename << EOF
# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2016  Walter Doekes, OSSO B.V.
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
from ..base import FuncBase


EOF
for cmd in "$@"; do
cat >> $filename << EOF
class $cmd(FuncBase):
    pass


EOF
done
cat >> $filename << EOF
def register(func_loader):
    for func in (
EOF
for cmd in "$@"; do
cat >> $filename << EOF
            $cmd,
EOF
done
cat >> $filename << EOF
            ):
        func_loader.register(func())
EOF
