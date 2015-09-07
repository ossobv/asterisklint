# vim: set ts=8 sw=4 sts=4 et ai:
from .config import ConfigAggregator
from .dialplan import DialplanAggregator
from .file import FileReader


# TODO: example modules.conf parser where load/noload/preload/autoload
#       are the only valid variables
# TODO: asterisk config lint
# TODO: asterisk dialplan lint
# TODO: delegate globals lintage to Config lint
# TODO: create the possibility for Asterisk version differences
# TODO: allow warnings to be suppressed? (always-emit, emit-once, silence)
# TODO: wat voor soort warnings: error (skip/ignore/fail), warning (case
#       fouten of schijnbaar/mogelijke inconsequentie)


class FileConfigParser(ConfigAggregator, FileReader):
    pass


class FileDialplanParser(DialplanAggregator, FileReader):
    pass
