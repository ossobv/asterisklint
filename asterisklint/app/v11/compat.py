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
from ..vall.builtin import register as builtin_register
from ..vall.unknown import register as unknown_register

from ..vall.app_cdr import register as app_cdr_register
from ..vall.app_celgenuserevent import register as app_celgenuserevent_register
from ..vall.app_chanisavail import register as app_chanisavail_register
from ..vall.app_channelredirect import register as app_channelredirect_register
from ..vall.app_chanspy import register as app_chanspy_register
from ..vall.app_confbridge import register as app_confbridge_register
from ..vall.app_dial import register as app_dial_register
from ..vall.app_directed_pickup import register as app_directed_pickup_register
from ..vall.app_dumpchan import register as app_dumpchan_register
from ..vall.app_echo import register as app_echo_register
from ..vall.app_exec import register as app_exec_register
from ..vall.app_forkcdr import register as app_forkcdr_register
from ..vall.app_macro import register as app_macro_register
from ..vall.app_meetme import register as app_meetme_register
from ..vall.app_mixmonitor import register as app_mixmonitor_register
from ..vall.app_page import register as app_page_register
from ..vall.app_playback import register as app_playback_register
from ..vall.app_queue import register as app_queue_register
from ..vall.app_read import register as app_read_register
from ..vall.app_record import register as app_record_register
from ..vall.app_sayunixtime import register as app_sayunixtime_register
from ..vall.app_setcallerid import register as app_setcallerid_register
from ..vall.app_stack import register as app_stack_register
from ..vall.app_system import register as app_system_register
from ..vall.app_userevent import register as app_userevent_register
from ..vall.app_verbose import register as app_verbose_register
from ..vall.app_voicemail import register as app_voicemail_register
from ..vall.app_waituntil import register as app_waituntil_register
from ..vall.chan_sip import register as chan_sip_register
from ..vall.res_fax import register as res_fax_register
from ..vall.res_indications import register as res_indications_register
from ..vall.res_musiconhold import register as res_musiconhold_register


def register(app_loader):
    for regfunc in (
            builtin_register,
            unknown_register,
            app_cdr_register,
            app_celgenuserevent_register,
            app_chanisavail_register,
            app_channelredirect_register,
            app_chanspy_register,
            app_confbridge_register,
            app_dial_register,
            app_directed_pickup_register,
            app_dumpchan_register,
            app_echo_register,
            app_exec_register,
            app_forkcdr_register,
            app_macro_register,
            app_meetme_register,
            app_mixmonitor_register,
            app_page_register,
            app_playback_register,
            app_queue_register,
            app_read_register,
            app_record_register,
            app_sayunixtime_register,
            app_setcallerid_register,
            app_stack_register,
            app_system_register,
            app_userevent_register,
            app_verbose_register,
            app_voicemail_register,
            app_waituntil_register,
            chan_sip_register,
            res_fax_register,
            res_indications_register,
            res_musiconhold_register):
        regfunc(app_loader)
