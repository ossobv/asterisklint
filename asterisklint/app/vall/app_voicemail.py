from ..base import AppBase


class VoiceMail(AppBase):
    pass


class VoiceMailMain(AppBase):
    pass


class MailboxExists(AppBase):
    pass


class VMAuthenticate(AppBase):
    pass


def register(app_loader):
    for app in (
            VoiceMail,
            VoiceMailMain,
            MailboxExists,
            VMAuthenticate,
            ):
        app_loader.register(app())
