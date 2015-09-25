#!/usr/bin/env python3
import sys

from asterisklint import FileDialplanParser


with open(sys.argv[1], 'rb') as extensions_conf:
    parser = FileDialplanParser(extensions_conf)
    dialplan = next(iter(parser))
    print(dialplan.format_as_dialplan_show())
