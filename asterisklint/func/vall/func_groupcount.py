from ..base import FuncBase


class GROUP(FuncBase):
    pass


class GROUP_COUNT(FuncBase):
    pass


class GROUP_LIST(FuncBase):
    pass


class GROUP_MATCH_COUNT(FuncBase):
    pass


def register(func_loader):
    for func in (
            GROUP,
            GROUP_COUNT,
            GROUP_LIST,
            GROUP_MATCH_COUNT,
            ):
        func_loader.register(func())
