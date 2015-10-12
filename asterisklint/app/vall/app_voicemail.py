from ..base import App, AppArg, AppOptions, AppBase


class VoiceMail(App):
    def __init__(self):
        super().__init__(
            # BUG: g takes an argument NUM.
            args=[AppArg('mailboxes'), AppOptions('bdgsuUP')], min_args=1)


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
