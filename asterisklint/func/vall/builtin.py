from ..base import FuncBase


class _Builtin(object):
    @property
    def module(self):
        return '<builtin>'


class BuiltinFuncBase(_Builtin, FuncBase):
    pass


class AMI_CLIENT(BuiltinFuncBase):
    pass


class EXCEPTION(BuiltinFuncBase):
    pass


class FEATURE(BuiltinFuncBase):
    pass


class FEATUREMAP(BuiltinFuncBase):
    pass


class MESSAGE(BuiltinFuncBase):
    pass


class MESSAGE_DATA(BuiltinFuncBase):
    pass


class TESTTIME(BuiltinFuncBase):
    pass


def register(func_loader):
    for func in (
            AMI_CLIENT, EXCEPTION, FEATURE, FEATUREMAP,
            MESSAGE, MESSAGE_DATA, TESTTIME):
        func_loader.register(func())
