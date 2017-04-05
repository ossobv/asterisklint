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
from importlib import import_module

from asterisklint.alinttest import ALintTestCase
from asterisklint.application import AppLoader


class AsteriskDpTest(ALintTestCase):
    """
    Test extensions.conf as supplied by Asterisk 13; after a few edits.
    """
    def test_extensions_conf(self):
        filename = __file__.rsplit('.', 1)[0] + '.conf'  # drop '.py[c]'

        # Hack to preserve chosen Background-case. This dialplan would
        # "unfix" the defaults for the other tests.
        background = AppLoader().get('background')
        chosen_spelling = background.chosen_spelling

        try:
            mainmod = import_module('asterisklint.commands.dialplan-check')
            mainmod.main([filename], {})

        finally:
            # Reset original Background-case.
            background.chosen_spelling = chosen_spelling

        self.assertLinted(
            {'I_NOTIMPL_IGNOREPAT': 3,
             'I_NOTIMPL_SWITCH': 1,
             'W_DP_GOTO_CONTEXT_NOEXTEN': 1,
             'W_DP_PRIO_BADORDER': 4})
