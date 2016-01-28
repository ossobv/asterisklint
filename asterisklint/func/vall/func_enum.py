from ..base import FuncBase


class ENUMQUERY(FuncBase):
    pass


class ENUMRESULT(FuncBase):
    pass


class ENUMLOOKUP(FuncBase):
    pass


class TXTCIDNAME(FuncBase):
    pass


def register(func_loader):
    for func in (
            ENUMQUERY, ENUMRESULT, ENUMLOOKUP, TXTCIDNAME):
        func_loader.register(func())
