# vim: set ts=8 sw=4 sts=4 et ai:
from importlib import import_module

from .defines import ErrorDef, WarningDef

# 1:
# # SOURCE: main/pbx.c: pbx_substitute_variables_helper_full
# die zoekt naar ${} of $[] en zoekt daarbinnen naar balanced } of resp. ]
# (zonder escaping), daarna wordt replacement gedaan:
# ${} => if endswith () => ast_func_read2, anders ast_str_retrieve_variable
# $[] =>


# 2: run app, bijv, Set, die een split doet, en dan dit:
# # int pbx_builtin_setvar_helper(struct ast_channel *chan,
#     const char *name, const char *value)
# L:                 return ast_func_write(chan, function, value);
# R:
#


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_APP_WSH(ErrorDef):
        message = 'whitespace before app {app!r} will result in unknown app'

    class E_APP_MISSING(ErrorDef):
        message = 'app {app!r} does not exist, dialplan will halt here!'

    class W_APP_BALANCE(WarningDef):
        message = ('app data {data!r} looks like unbalanced'
                   'parenthesis/quotes/curlies')

    class W_APP_BAD_CASE(WarningDef):
        message = 'app {app!r} does not have the proper Case {proper!r}'

    class W_APP_NEED_PARENS(WarningDef):
        message = 'app {app!r} should have parentheses (only NoOp is exempt)'

    class W_APP_WSH(ErrorDef):
        message = 'unexpected whitespace after app {app!r}'


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AppLoader(metaclass=Singleton):
    def __init__(self, version='v11'):
        self.version = version
        self._version_dirs = (version, 'vall')
        self._lower_apps = {}

    def get(self, lower_app):
        # Attempt to load .version.app.register(). If it doesn't exist,
        # we attempt to load .version.default.register(). It should
        # exist.
        if lower_app not in self._lower_apps:
            if not self.load(lower_app):
                self.get('default')  # ensure default exists
                # The default may have loaded more apps. Check it and
                # only alias the other app to default if it didn't.
                if lower_app not in self._lower_apps:
                    # TODO: we may want to warn here, but we have no
                    # Where()
                    self._lower_apps[lower_app] = self._lower_apps['default']

            assert lower_app in self._lower_apps
        return self._lower_apps[lower_app]

    def load(self, lower_app):
        for version in self._version_dirs:
            mod_name = 'asterisklint.app.{}.{}'.format(version, lower_app)
            try:
                app_handler = import_module(mod_name)
            except ImportError as e:
                if (e.args[0] == "No module named '{}'".format(mod_name) and
                        mod_name != 'asterisklint.apps.vall.default'):
                    pass
                else:
                    raise
            else:
                app_handler.register(self)
                return True
        return False

    def register(self, app):
        lower_app = app.name.lower()
        self._lower_apps[lower_app] = app


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
        """
        Parse self.raw into an App and data. Recursively replaces the
        app data as far as possible.

        It tries to find a specific handler for the application, but
        will fall back to a default handler (parse_simple) if it cannot
        be found.
        """
        # Fetch the Application. If we don't know specifically, we can
        # call the parse_simple on it.
        if not self.split_app_data():
            return

        # Find the handler from the registered handlers. If there is no
        # custom handler, we may already raise a message here.
        app = AppLoader().get(self.app_lower)

        # Pass the data through a handler -- which also handles
        # functions -- first:
        # SOURCE: main/pbx.c: pbx_substitute_variables_helper_full
        # TODO: here..
        self.data = self.data  # this stuff..

        # Check app availability.
        if app.name != self.app:
            if app.name == 'Default':
                E_APP_MISSING(self.where, app=self.app)
            else:
                W_APP_BAD_CASE(self.where, app=self.app, proper=app.name)

        # Run data through app.
        app(self.data, where=self.where)

    def split_app_data(self):
        """
        Splits self.raw into self.app, self.app_lower, self.data.
        """
        try:
            app, data = self.raw.split('(', 1)
        except ValueError:
            # We allow NoOp without parentheses. The others need parens.
            app = self.raw
            if self.raw.lower() != 'noop':
                W_APP_NEED_PARENS(self.where, app=app)
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
            return False
        if self.app.lstrip() != self.app:
            W_APP_WSH(self.where)
            self.app = self.app.lstrip()
            self.app_lower = self.app.lower()
        # Quick check that the app doesn't exist.
        if not self.app:
            E_APP_MISSING(self.where)
            return False

        return True

    @property
    def name(self):
        return self.app
