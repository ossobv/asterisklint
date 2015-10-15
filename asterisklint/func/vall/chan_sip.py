from ..base import FuncBase


class CHECKSIPDOMAIN(FuncBase):
    pass


class SIP_HEADER(FuncBase):
    pass


class SIPCHANINFO(FuncBase):
    pass


class SIPPEER(FuncBase):
    pass


def register(func_loader):
    for func in (
            CHECKSIPDOMAIN, SIP_HEADER,
            SIPCHANINFO, SIPPEER):
        func_loader.register(func())
