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
from tempfile import NamedTemporaryFile
from importlib import import_module

from asterisklint.alinttest import ALintTestCase, ignoreLinted
from asterisklint.application import AppLoader


class BackgroundCaseTest(ALintTestCase):
    """
    Background may be spelled as BackGround or Background.

    The official spelling is BackGround, but that's just plain horrible.
    Allow the user to choose one and stick with it.
    """

    def _dialplan_check(self, dialplan):
        # Hack to preserve chosen Background-case.
        background = AppLoader().get('background')
        chosen_spelling = background.chosen_spelling

        try:
            fp = NamedTemporaryFile()  # auto-deleted, works in testcase
            fp.write(dialplan.encode('utf-8'))
            fp.flush()

            mainmod = import_module('asterisklint.commands.dialplan-check')
            mainmod.main([fp.name], {})

        finally:
            # Reset original Background-case.
            background.chosen_spelling = chosen_spelling

    @ignoreLinted('H_*')
    def test_better_Background_no_warn(self):
        self._dialplan_check('''\
[context]
exten => s,1,Background(abc)
exten => s,n,Background(abc)
exten => s,n,Background(abc)
''')

    @ignoreLinted('H_*')
    def test_official_BackGround_no_warn(self):
        self._dialplan_check('''\
[context]
exten => s,1,BackGround(abc)
exten => s,n,BackGround(abc)
exten => s,n,BackGround(abc)
''')

    @ignoreLinted('H_*')
    def test_better_Background_warn_once(self):
        self._dialplan_check('''\
[context]
exten => s,1,Background(abc)
exten => s,n,BackGround(abc)
exten => s,n,Background(abc)
''')
        self.assertLinted({'W_APP_BAD_CASE': 1})

    @ignoreLinted('H_*')
    def test_official_BackGround_warn_twice(self):
        self._dialplan_check('''\
[context]
exten => s,1,BackGround(abc)
exten => s,n,Background(abc)
exten => s,n,Background(abc)
''')
        self.assertLinted({'W_APP_BAD_CASE': 2})
