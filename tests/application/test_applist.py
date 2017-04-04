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
from asterisklint.alinttest import ALintTestCase, GenerateTestCases
from asterisklint.application import App
from asterisklint.where import DUMMY_WHERE

APPLICATION_LIST = (
    'AGI', 'AddQueueMember', 'Answer', 'Authenticate', 'Background',
    'Busy', 'CELGenUserEvent', 'ChanIsAvail',
    'ChanSpy', 'ChannelRedirect', 'ConfBridge', 'Congestion',
    'ControlPlayback',
    'DateTime', 'Dial', 'DumpChan', 'Echo', 'Exec',
    'ExtenSpy', 'ForkCDR', 'Gosub', 'Goto',
    'Hangup', 'ImportVar', 'Log', 'Macro',
    'MacroExclusive', 'MacroExit', 'MacroIf', 'MailboxExists', 'MeetMe',
    'MeetMeAdmin', 'MeetMeChannelAdmin', 'MeetMeCount', 'MixMonitor',
    'MusicOnHold', 'NoCDR', 'NoOp', 'Page', 'PauseQueueMember',
    'Pickup', 'PickupChan', 'PickupOld1v4', 'PlayTones', 'Playback',
    'Proceeding', 'Progress', 'Queue', 'QueueLog', 'Read', 'ReceiveFAX',
    'Record', 'RemoveQueueMember', 'ResetCDR', 'RetryDial', 'Return',
    'Ringing', 'SIPAddHeader', 'SIPDtmfMode', 'SIPRemoveHeader',
    'SLAStation', 'SLATrunk', 'SayAlpha', 'SayDigits', 'SayNumber',
    'SayPhonetic', 'SayUnixTime', 'SendFAX', 'SetAMAFlags',
    'SetCallerID', 'SetCallerPres', 'SetGlobalVar', 'SetMusicOnHold',
    'StackPop', 'StartMusicOnHold', 'StopMixMonitor', 'StopMusicOnHold',
    'StopPlayTones', 'System', 'TryExec', 'TrySystem', 'Unknown',
    'UnpauseQueueMember', 'UserEvent', 'VMAuthenticate', 'Verbose',
    'VMSayName', 'VoiceMail', 'VoiceMailMain', 'VoiceMailPlayMsg',
    'Wait', 'WaitExten',
    'WaitMusicOnHold', 'WaitUntil',

    # These are skipped from the test because they require certain
    # syntax for the arguments.
    # 'ExecIfTime', 'GosubIfTime', 'GotoIfTime', 'Set',
)


class ApplicationListTest(ALintTestCase, metaclass=GenerateTestCases(
        '_test_template', [(i,) for i in APPLICATION_LIST])):
    "Test that a bunch of applications exist."

    def test_Goto(self):
        "Test that Application 'Goto' exists."
        App('Goto(random_argument)', where=DUMMY_WHERE)

    def _test_template(self, application):
        "Test that Application '{}' exists (generated test)."
        App('{}(random_argument)'.format(application), where=DUMMY_WHERE)
