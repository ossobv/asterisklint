#!/usr/bin/env python3
"""
Show which variables are used by the dialplan.
"""
import sys

from asterisklint import FileDialplanParser
from asterisklint.varfun import VarLoader


loader = VarLoader()
parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))

print('Variables encountered:')
for variable, occurrences in sorted(
        loader._variables.items(), key=(lambda x: x[0].lower())):
    print('  {:20}  [{} times in {} files]'.format(
        variable, len(occurrences),
        len(set(i.filename for i in occurrences))))
