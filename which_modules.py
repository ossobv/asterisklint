#!/usr/bin/env python3
import sys

from asterisklint import FileDialplanParser
from asterisklint.application import AppLoader


with open(sys.argv[1], 'rb') as extensions_conf:
    loader = AppLoader(version='v11')  # example setting the version
    parser = FileDialplanParser(extensions_conf)
    dialplan = next(iter(parser))
    print('Application providing modules used:')
    for module in loader.used_modules:
        print(' ', module)
