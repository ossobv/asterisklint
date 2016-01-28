# vim: set ts=8 sw=4 sts=4 et ai:
from .config import ConfigAggregator
from .dialplan import DialplanAggregator
from .file import FileReader


class FileConfigParser(ConfigAggregator, FileReader):
    pass


class FileDialplanParser(DialplanAggregator, FileReader):
    pass
