import sys

from asterisklint import FileDialplanParser


c = FileDialplanParser(sys.argv[1])
dialplan = next(iter(c))
print(dialplan.format_as_dialplan_show())
