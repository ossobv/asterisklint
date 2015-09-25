from ..base import AppBase


class SIPAddHeader(AppBase):
    pass


class SIPDtmfMode(AppBase):
    pass


def register(app_loader):
    app_loader.register(SIPAddHeader())
    app_loader.register(SIPDtmfMode())
