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
from functools import partial

from asterisklint.alinttest import ALintTestCase
from asterisklint.app.vall.app_voicemail import VoiceMail
from asterisklint.where import DUMMY_WHERE


class VoiceMailArgsTest(ALintTestCase):
    def setUp(self):
        super().setUp()
        ignored = []
        self.v = partial(
            VoiceMail(), jump_destinations=ignored, where=DUMMY_WHERE)

    def test_one_arg(self):
        self.v('mailbox@context')

    def test_two_args(self):
        self.v('mailbox@context,bd')

    def test_min_args(self):
        self.v('')  # 0 args, no good
        self.assertLinted({'E_APP_ARG_FEW': 1})

    def test_max_args(self):
        self.v('a,,c')  # 3 args, no good
        self.assertLinted({'E_APP_ARG_MANY': 1})

    def test_bad_option(self):
        self.v('a,X')  # 2nd arg has bad option
        self.assertLinted({'E_APP_ARG_BADOPT': 1})

    def test_dupe_option(self):
        self.v('a,bdb')  # 2nd arg has duplicate option
        self.assertLinted({'E_APP_ARG_DUPEOPT': 1})
