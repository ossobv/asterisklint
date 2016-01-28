from ..base import AppBase


class SIPAddHeader(AppBase):
    pass


class SIPRemoveHeader(AppBase):
    pass  # not in v1.4


class SIPDtmfMode(AppBase):
    pass


def register(app_loader):
    for app in (
            SIPAddHeader, SIPRemoveHeader, SIPDtmfMode):
        app_loader.register(app())
