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
"""
Subject: walk_jump_destinations: UnboundLocalError: local variable 'i'
  referenced before assignment #7
Source: https://github.com/ossobv/asterisklint/issues/7
"""
from tempfile import NamedTemporaryFile
from importlib import import_module

from asterisklint.alinttest import ALintTestCase, ignoreLinted


class Github7TestCase(ALintTestCase):
    @ignoreLinted('*')  # ignore validity, we just don't want crashes
    def test_bug(self):
        dialplan = NamedTemporaryFile()  # auto-deleted, works in testcase
        dialplan.write(b'''\
[context]
; The EXTEN:1 tries to slice "s", which returns "". We don't want
; crashes because of that.
exten => s,1,GotoIf($["${CALLERID(num):0:1}"="+"]?${EXTEN:1},1)
''')
        dialplan.flush()

        mainmod = import_module('asterisklint.commands.dialplan-check')
        mainmod.main([dialplan.name], {'ALINT_IGNORE': '*'})
