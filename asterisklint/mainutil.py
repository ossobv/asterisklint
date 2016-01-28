import argparse
import os

from . import FileFuncOdbcParser


class UniqueStore(argparse.Action):
    "Make sure an --argument is only used at most once."
    def __call__(self, parser, namespace, values, option_string):
        if getattr(namespace, self.dest, self.default) is not None:
            parser.error("{} appears several times".format(option_string))
        setattr(namespace, self.dest, values)


def load_func_odbc_functions(func_odbc_arg, dialplan_arg):
    if func_odbc_arg == '':
        # Explicit disable.
        return

    if func_odbc_arg is None:
        # Auto-detect?
        func_odbc_arg = os.path.join(
            os.path.dirname(dialplan_arg), 'func_odbc.conf')
        if not os.path.exists(func_odbc_arg):
            # If there is no such file, don't worry about it.
            return

    # Load it up.
    # TODO: do we want to silence func_odbc errors/warnings here?
    parser = FileFuncOdbcParser()
    parser.include(func_odbc_arg)
    for func_odbc_context in parser:
        pass
