from ..vall.builtin import register as builtin_register
from ..vall.unknown import register as unknown_register

from ..vall.app_dial import register as app_dial_register
from ..vall.app_dumpchan import register as app_dumpchan_register
from ..vall.app_exec import register as app_exec_register
from ..vall.app_playback import register as app_playback_register
from ..vall.app_stack import register as app_stack_register
from ..vall.app_verbose import register as app_verbose_register
from ..vall.chan_sip import register as chan_sip_register
from ..vall.res_musiconhold import register as res_musiconhold_register


def register(app_loader):
    for regfunc in (
            builtin_register,
            unknown_register,
            app_dial_register,
            app_dumpchan_register,
            app_exec_register,
            app_playback_register,
            app_stack_register,
            app_verbose_register,
            chan_sip_register,
            res_musiconhold_register):
        regfunc(app_loader)
