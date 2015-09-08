# vim: set ts=8 sw=4 sts=4 et ai:
from .defines import ErrorDef, WarningDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_APP_WSH(ErrorDef):
        message = 'whitespace before app will result in unknown app'

    class E_APP_MISSING(ErrorDef):
        message = 'app does not exist, dialplan will halt here!'

    class W_APP_BALANCE(WarningDef):
        message = 'looks like unbalanced parenthesis/quotes/curlies'

    class W_APP_NEED_PARENS(WarningDef):
        message = 'all applications except NoOp should have parentheses'

    class W_APP_WSH(ErrorDef):
        message = 'unexpected whitespace after app'


class App(object):
    # App heeft weer z'n eigen parsers en subparsers. Hiermee moeten we ook
    # op kunnen zoeken welke modules er nodig zijn (w00t). Deze komt ook als
    # eerste in aanmerking voor 1.4 vs. 1.8 differences (ExecIf..., vs
    # ExecIf...?)
    # Ook dumpen van alle variabelen (in dat geval moet de subparser aangeven
    # dat een Var geset wordt (Set() en MSet() doen dat bijv.) en ARRAY() en
    # HASH().
    # Parser en subparsers implementeren volgens included modules?
    # Klinkt wat overkill? Maar maakt het wel mooi extensible. De ExecIf()
    # kan dan de args weer splitten en teruggeven...
    #
    # Per subparser kunnen we de versienummers opgeven:
    # SPRINTF() voor < 1.2 => None
    # SPRINTF() voor >= 1.2 < 1.4 => behaviour X
    # SPRINTF() voor >= 1.4 => behaviour Y
    #
    # Hoe pakken we dan app_compat settings voor Set? Hm.
    def __init__(self, app, where):
        # FIXME: parse app
        self.raw = app
        self.where = where

        # Attempt to parse the app + data.
        self.parse()

    def parse(self):
        # Fetch the Application. If we don't know specifically, we can
        # call the parse_simple on it.
        try:
            app, data = self.raw.split('(', 1)
        except ValueError:
            # We allow NoOp without parentheses. The others need parens.
            app = self.raw
            if self.raw.lower() != 'noop':
                W_APP_NEED_PARENS(self.where)
            data = '()'
        else:
            data = '(' + data

        # SOURCE: pbx/pbx_config.c: pbx_load_config()
        if data.startswith('(') and data.endswith(')'):
            data = data[1:-1]
        else:
            W_APP_NEED_PARENS(self.where)

        # Set it and try to find a handler for it.
        self.app = app
        self.app_lower = app.lower()
        self.data = data

        # Leading whitespace is frowned upon but allowed. Trailing
        # whitespace won't work:
        if self.app.rstrip() != self.app:
            E_APP_WSH(self.where)
            return
        if self.app.lstrip() != self.app:
            W_APP_WSH(self.where)
            self.app = self.app.lstrip()
            self.app_lower = self.app.lower()
        # Quick check that the app doesn't exist.
        if not self.app:
            E_APP_MISSING(self.where)
            return

        # Pass the data through a handler -- which also handles
        # functions -- first:
        # SOURCE: main/pbx.c: pbx_substitute_variables_helper_full
        # TODO: here..

        # Find handler from the registered handlers and use that.  If
        # there is no registered handler, fall back to a simpler parser
        # that checks quotes and tries to extract variables names
        # anyway. (XXX?)
        handler = self.get_handler()
        if handler:
            handler(self)
        else:
            self.default_handler()

    def get_handler(self):
        # load app_set from app_builtin
        # self.app_lower == 'set':
        return

    def default_handler(self):
        try:
            self.check_balance(self.data)
        except ValueError:
            W_APP_BALANCE(self.where)
        # TODO: extract variables

    @staticmethod
    def check_balance(app):
        # TODO: we don't check backslash escapes here, should we?
        # TODO: write proper tests for this?
        arr = ['X']
        for char in app:
            if char == '"':
                if arr[-1] == '"':
                    arr.pop()
                elif arr[-1] == "'":
                    pass
                else:
                    arr.append('"')
            elif char == "'":
                if arr[-1] == "'":
                    arr.pop()
                elif arr[-1] == '"':
                    pass
                else:
                    arr.append("'")
            elif char in '({[':
                if arr[-1] in '\'"':
                    pass
                else:
                    arr.append(char)
            elif char in ')}]':
                left = '({['[')}]'.index(char)]
                if arr[-1] in '\'"':
                    pass
                else:
                    if arr[-1] == left:
                        arr.pop()
                    else:
                        raise ValueError(''.join(arr[1:]))
        if arr != ['X']:
            raise ValueError(''.join(arr[1:]))
