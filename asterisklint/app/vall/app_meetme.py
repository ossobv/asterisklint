from ..base import AppBase


class MeetMe(AppBase):
    pass


class MeetMeCount(AppBase):
    pass


class MeetMeAdmin(AppBase):
    pass


class MeetMeChannelAdmin(AppBase):
    pass


class SLAStation(AppBase):
    pass


class SLATrunk(AppBase):
    pass


def register(app_loader):
    for app in (
            MeetMe,
            MeetMeCount,
            MeetMeAdmin,
            MeetMeChannelAdmin,
            SLAStation,
            SLATrunk,
            ):
        app_loader.register(app())
