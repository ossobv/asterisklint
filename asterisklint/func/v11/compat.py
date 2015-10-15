from ..vall.builtin import register as builtin_register
from ..vall.unknown import register as unknown_register

from ..vall.chan_sip import register as chan_sip_register
from ..vall.func_callerid import register as func_callerid_register
from ..vall.func_cdr import register as func_cdr_register
from ..vall.func_channel import register as func_channel_register
from ..vall.func_curl import register as func_curl_register
from ..vall.func_cut import register as func_cut_register
from ..vall.func_logic import register as func_logic_register
from ..vall.func_math import register as func_math_register
from ..vall.func_strings import register as func_strings_register


def register(func_loader):
    for regfunc in (
            builtin_register,
            unknown_register,
            chan_sip_register,
            func_callerid_register,
            func_cdr_register,
            func_channel_register,
            func_curl_register,
            func_cut_register,
            func_logic_register,
            func_math_register,
            func_strings_register):
        regfunc(func_loader)
