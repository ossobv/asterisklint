from ..base import FuncBase


class QUEUE_EXISTS(FuncBase):
    pass


class QUEUE_MEMBER(FuncBase):
    pass


class QUEUE_MEMBER_COUNT(FuncBase):
    pass


class QUEUE_MEMBER_LIST(FuncBase):
    pass


class QUEUE_MEMBER_PENALTY(FuncBase):
    pass


class QUEUE_VARIABLES(FuncBase):
    pass


class QUEUE_WAITING_COUNT(FuncBase):
    pass


def register(func_loader):
    for func in (
            QUEUE_EXISTS, QUEUE_MEMBER, QUEUE_MEMBER_COUNT,
            QUEUE_MEMBER_LIST, QUEUE_MEMBER_PENALTY,
            QUEUE_VARIABLES, QUEUE_WAITING_COUNT):
        func_loader.register(func())
