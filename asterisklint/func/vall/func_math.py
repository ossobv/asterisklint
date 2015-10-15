from ..base import FuncBase
from ...varfun import VarLoader


class MATH(FuncBase):
    pass


class INC(FuncBase):
    """
    INC takes a single varname as argument. That means we can count the
    variable as used.
    """
    def __call__(self, data, where):
        ret = super().__call__(data, where)
        VarLoader().count_var(data, where)
        return ret


class DEC(FuncBase):
    """
    DEC takes a single varname as argument. That means we can count the
    variable as used.
    """
    def __call__(self, data, where):
        ret = super().__call__(data, where)
        VarLoader().count_var(data, where)
        return ret


def register(func_loader):
    for func in (
            MATH, INC, DEC):
        func_loader.register(func())
