import os

from .cls import Singleton


class AsteriskVersion(metaclass=Singleton):
    """
    Store the used Asterisk version globally. If you don't initialize
    this before anyone requests anything, you get the default.

    Example::

        from asterisklint.version import AsteriskVersion

        AsteriskVersion('v11')  # set version 11 throughout the run
    """
    DEFAULT = 'v11'

    def __init__(self, version=None):
        self.version = version or self.DEFAULT

    def reinit(self, version=None):
        if version and self.version != version:
            raise RuntimeError(
                'Attempt to re-set Asterisk version from {} to {}'.format(
                    self.version, version))

    def list_app_mods(self):
        """
        Return a list app names in absolute import format. Takes
        internal version into account.
        """
        return self._list_mods('app')

    def list_func_mods(self):
        """
        Return a list function names in absolute import format. Takes
        internal version into account.
        """
        return self._list_mods('func')

    def _get_path(self, submod):
        return os.path.join(os.path.dirname(__file__), submod, self.version)

    def _list_mods(self, submod):
        appsdir = self._get_path(submod)
        appmods = [i[0:-3] for i in os.listdir(appsdir) if i.endswith('.py')]

        modfmt = 'asterisklint.{}.{}.{{}}'.format(submod, self.version)
        return [modfmt.format(appmod) for appmod in appmods]
