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

from ..vall.app_confbridge import register as app_confbridge_register
from ..vall.app_queue import register as app_queue_register
from ..vall.chan_sip import register as chan_sip_register
from ..vall.func_callerid import register as func_callerid_register
from ..vall.func_cdr import register as func_cdr_register
from ..vall.func_channel import register as func_channel_register
from ..vall.func_curl import register as func_curl_register
from ..vall.func_cut import register as func_cut_register
from ..vall.func_enum import register as func_enum_register
from ..vall.func_env import register as func_env_register
from ..vall.func_global import register as func_global_register
from ..vall.func_groupcount import register as func_groupcount_register
from ..vall.func_logic import register as func_logic_register
from ..vall.func_math import register as func_math_register
from ..vall.func_rand import register as func_rand_register
from ..vall.func_shell import register as func_shell_register
from ..vall.func_strings import register as func_strings_register
from ..vall.func_uri import register as func_uri_register
from ..vall.res_fax import register as res_fax_register


def register(func_loader):
    for regfunc in (
            builtin_register,
            unknown_register,
            app_confbridge_register,
            app_queue_register,
            chan_sip_register,
            func_callerid_register,
            func_cdr_register,
            func_channel_register,
            func_curl_register,
            func_cut_register,
            func_enum_register,
            func_env_register,
            func_global_register,
            func_groupcount_register,
            func_logic_register,
            func_math_register,
            func_rand_register,
            func_shell_register,
            func_strings_register,
            func_uri_register,
            res_fax_register):
        regfunc(func_loader)
