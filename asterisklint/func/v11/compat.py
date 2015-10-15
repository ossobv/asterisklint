from ..vall.builtin import register as builtin_register
from ..vall.unknown import register as unknown_register

from ..vall.chan_sip import register as chan_sip_register
from ..vall.func_curl import register as func_curl_register
from ..vall.func_math import register as func_math_register


def register(func_loader):
    for regfunc in (
            builtin_register,
            unknown_register,
            chan_sip_register,
            func_curl_register,
            func_math_register):
        regfunc(func_loader)
