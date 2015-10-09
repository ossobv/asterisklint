#!/usr/bin/env python3
import sys

from asterisklint import FileDialplanParser
from asterisklint.application import VarsLoader


loader = VarsLoader()
parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))

print('Variables encountered:')
for variable, occurrences in sorted(
        loader._variables.items(), key=(lambda x: x[0].lower())):
    print('  {:20}  [{} times in {} files]'.format(
        variable, len(occurrences),
        len(set(i.filename for i in occurrences))))
