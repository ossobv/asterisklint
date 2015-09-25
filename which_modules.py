#!/usr/bin/env python3
import sys

from asterisklint import FileDialplanParser
from asterisklint.application import AppLoader


loader = AppLoader(version='v11')  # example setting the version
parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))
print('Application providing modules used:')
for module in loader.used_modules:
    print(' ', module)
