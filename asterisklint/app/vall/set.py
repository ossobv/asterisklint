from .default import Default


class Set(Default):
    pass


def register(app_loader):
    # Called by the app_loader.
    app_loader.register(Set())
