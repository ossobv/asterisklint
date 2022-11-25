# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2016-2017  Walter Doekes, OSSO B.V.
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
"""
from tempfile import NamedTemporaryFile
from importlib import import_module

from asterisklint.alinttest import ALintTestCase, ignoreLinted


class GithubIssuesTestCase(ALintTestCase):
    def check_dialplan(self, dialplan):
        dp = NamedTemporaryFile()  # auto-deleted, works in testcase
        dp.write(dialplan.encode('utf-8'))
        dp.flush()

        mainmod = import_module('asterisklint.commands.dialplan-check')
        mainmod.main([dp.name], {})

    def check_func_odbc_conf(self, func_odbc_conf):
        dp = NamedTemporaryFile()  # auto-deleted, works in testcase
        dp.write(func_odbc_conf.encode('utf-8'))
        dp.flush()

        mainmod = import_module('asterisklint.commands.func_odbc-check')
        mainmod.main([dp.name], {})

    @ignoreLinted('*')  # ignore validity, we just don't want crashes
    def test_issue_7(self):
        """
        Subject: walk_jump_destinations: UnboundLocalError: local variable 'i'
          referenced before assignment
        Source: https://github.com/ossobv/asterisklint/issues/7
        """
        return self.check_dialplan('''\
[context]
; The EXTEN:1 tries to slice "s", which returns "". We don't want
; crashes because of that.
exten => s,1,GotoIf($["${CALLERID(num):0:1}"="+"]?${EXTEN:1},1)
''')

    @ignoreLinted('H_*')
    def test_issue_17(self):
        """
        Subject: varfun: AttributeError: 'list' object has no attribute 'split'
        Source: https://github.com/ossobv/asterisklint/issues/17
        """
        return self.check_dialplan('''\
[context]
; The argument to SET() should be a Var-list, not a regular list.
exten => s,1,While($["${SET(languagenumber=${SHIFT(languages)})}" != ""])
''')

    @ignoreLinted('H_*')
    def test_issue_41(self):
        """
        Subject: E_APP_ARG_MANY gosub freeze endless check with 100% cpu
        Source: https://github.com/ossobv/asterisklint/issues/41
        """
        self.check_dialplan('''\
[context]
; Don't choke on the excess comma after prio 1.
exten => _7495XXXXXXX,1,GosubIf(${Q}?\
sub-dial,${EXTEN},1,(${SOME_VARIABLE}):\
sub-dial,${EXTEN},1,(${SOME_VARIABLE}))
exten => _7495XXXXXXX,n(x),Gosub(sub-dial,${EXTEN},1,(${SOME_VARIABLE}))
''')
        self.assertLinted({'E_APP_ARG_MANY': 3, 'E_DP_GOTO_NOCONTEXT': 3})

    @ignoreLinted(
        'H_DP_GENERAL_MISPLACED', 'H_DP_GLOBALS_MISPLACED', 'I_NOTIMPL_HINT')
    def test_issue_54(self):
        """
        Subject: W_ARROW wasn't implemented and basic-pbx samples used it
        Source: https://github.com/ossobv/asterisklint/issues/54
        """
        self.check_dialplan('''\
[Hints]
; Don't die even though there is no arrow. Source: asterisk/asterisk
; 2cfb3df35df7930541177eb32d71afa52cd38899 configs/basic-pbx/extensions.conf
exten => _10XX,hint,PJSIP/${EXTEN}
exten = _11XX,hint,PJSIP/${EXTEN}
''')
        self.assertLinted({
            'H_CONF_NO_ARROW': 1,   # expected " => ", got " = "
            'W_WSH_VARSET': 1,      # expected "=", got " = "
        })

    def test_issue_54_func_odbc(self):
        """
        Subject: W_ARROW wasn't implemented (here we expect equals, not arrow)
        """
        self.check_func_odbc_conf('''\
[PRESENCE]
writehandle=mysql1
readsql => SELECT location FROM presence WHERE id='${SQL_ESC(${ARG1})}'
writesql => UPDATE presence SET location='${SQL_ESC(${VAL1})}'\
 WHERE id='${SQL_ESC(${ARG1})}'
''')
        self.assertLinted({'H_CONF_HAS_ARROW': 2})

    @ignoreLinted('H_*')
    def test_issue_via_gamma_20221019(self):
        self.check_dialplan('''\
[context]
exten => _3112345!,1,ExecIf(\
$["${preferred_number}"!=""]?\
Set(CDR(userfield)=\
${CDR(userfield):0:${userfield_skip}}${preferred_number}\
${CDR(userfield):${MATH(${userfield_skip}+${LEN(${preferred_number})},int)}}\
)\
)
''')
