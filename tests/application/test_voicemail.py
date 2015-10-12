from asterisklint.alinttest import ALintTestCase
from asterisklint.app.vall.app_voicemail import VoiceMail
from asterisklint.where import DUMMY_WHERE


class VoiceMailArgsTest(ALintTestCase):
    def setUp(self):
        super().setUp()
        self.v = VoiceMail()

    def test_one_arg(self):
        self.v('mailbox@context', DUMMY_WHERE)

    def test_two_args(self):
        self.v('mailbox@context,bd', DUMMY_WHERE)

    def test_min_args(self):
        self.v('', DUMMY_WHERE)  # 0 args, no good
        self.assertLinted({'E_APP_ARG_FEW': 1})

    def test_max_args(self):
        self.v('a,,c', DUMMY_WHERE)  # 3 args, no good
        self.assertLinted({'E_APP_ARG_MANY': 1})

    def test_bad_option(self):
        self.v('a,X', DUMMY_WHERE)  # 2nd arg has bad option
        self.assertLinted({'E_APP_ARG_BADOPT': 1})

    def test_dupe_option(self):
        self.v('a,bdb', DUMMY_WHERE)  # 2nd arg has duplicate option
        self.assertLinted({'E_APP_ARG_DUPEOPT': 1})
