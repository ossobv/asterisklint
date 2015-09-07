# vim: set ts=8 sw=4 sts=4 et ai:
from .defines import WarningDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class W_APP_BALANCE(WarningDef):
        message = 'looks like unbalanced parenthesis/quotes/curlies'


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

        # Attempt to parse the app.
        self.parse()

    def parse(self):
        # Fetch the Application. If we don't know specifically, we can
        # call the parse_simple on it.
        # FIXME: try to find a proper handler first (Set?)
        try:
            self.parse_simple(self.raw)
        except ValueError:
            W_APP_BALANCE(self.where)

    @staticmethod
    def parse_simple(app):
        # TODO: we don't check backslash escapes here
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
