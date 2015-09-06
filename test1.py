import sys

from asterisklint import FileDialplanParser


c = FileDialplanParser(sys.argv[1])
for context in c:
    # Are we in dialplan? Then parse stuff a bit differently.. by upgrading
    # the Context to a DialplanContext and the Varset to an Extension.
    print(context)
