from ..base import AppBase


class Queue(AppBase):
    pass


class AddQueueMember(AppBase):
    pass


class RemoveQueueMember(AppBase):
    pass


class PauseQueueMember(AppBase):
    pass


class UnpauseQueueMember(AppBase):
    pass


class QueueLog(AppBase):
    pass


def register(app_loader):
    for app in (
            Queue,
            AddQueueMember,
            RemoveQueueMember,
            PauseQueueMember,
            UnpauseQueueMember,
            QueueLog,
            ):
        app_loader.register(app())
