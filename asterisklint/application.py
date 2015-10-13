# vim: set ts=8 sw=4 sts=4 et ai:
import os
import string
from collections import defaultdict
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

    class E_APP_PARSE_ERROR(ErrorDef):
        message = 'app {app!r} arguments {args!r} raise a parse error'

    class W_APP_BALANCE(WarningDef):
        message = ('app data {data!r} looks like unbalanced'
                   'parenthesis/quotes/curlies')

    class W_APP_BAD_CASE(WarningDef):
        message = 'app {app!r} does not have the proper Case {proper!r}'

    class W_APP_NEED_PARENS(WarningDef):
        message = 'app {app!r} should have parentheses (only NoOp is exempt)'

    class W_APP_WSH(ErrorDef):
        message = 'unexpected whitespace after app {app!r}'


class ParseError(ValueError):
    pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Variable(object):
    """
    A single variable, or a list of variables and literals.
    """
    @classmethod
    def join(self, variables):
        copy = []
        for var in variables:
            if not isinstance(var, (str, Variable)):
                raise TypeError(
                    'Variables can only consist of strings and variables, '
                    'got {!r}'.format(var))
            if var:
                copy.append(var)

        if len(copy) == 0:
            return ''
        if len(copy) == 1:
            return copy[0]

        # Use private setter instead of constructor.
        ret = Variable()
        ret._list = copy
        return ret

    def __init__(self, name=None):
        self.name = name

    def format(self, **kwargs):
        if self.name is None:
            ret = []
            for var in self._list:
                if isinstance(var, str):
                    ret.append(var)
                else:
                    ret.append(var.format(**kwargs))
            return ''.join(ret)

        elif isinstance(self.name, Variable):
            ret = self.name.format(**kwargs)
            return kwargs[ret]

        else:
            return kwargs[self.name]

    def __iter__(self):
        """
        You may iterate over this thing, as if it where a string. In
        which case you get the literal letters, and Variables in
        between.
        """
        return iter(self._get_cached_iter())

    def __getitem__(self, *args, **kwargs):
        return self._get_cached_iter().__getitem__(*args, **kwargs)

    def _get_cached_iter(self):
        if not hasattr(self, '_cached_iter'):
            ret = []
            if self.name is None:
                for var in self._list:
                    for inner in var:
                        ret.append(inner)
            else:
                ret.append(self)
            self._cached_iter = ret
        return self._cached_iter

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False

        if (self.name, other.name) == (None, None):
            if len(self._list) != len(other._list):
                return False
            return all(self._list[i] == other._list[i]
                       for i in range(len(self._list)))

        if None in (self.name, other.name):
            return False

        return self.name == other.name

    def __str__(self):
        if self.name:
            return '${{{}}}'.format(self.name)
        return ''.join(str(i) for i in self._list)


class VarsLoader(metaclass=Singleton):
    def __init__(self, version='v11'):
        self.version = version
        self._variables = defaultdict(list)

    def substitute_variables(self, data, where):
        """
        We cannot pretend to know what the variables will hold, but we
        do know that certain function return certain types of
        information. We can attempt to replace things as appropriate.
        """
        ret = []
        beginpos = searchpos = 0
        while True:
            try:
                pos = data.index('$', searchpos)
                next_ = data[pos + 1]
            except (IndexError, ValueError):
                ret.append(data[beginpos:])
                break
            else:
                if next_ in '{[':
                    ret.append(data[beginpos:pos])
                    if next_ == '{':
                        endpos, more_substitutions = self._find_brackets_end(
                            data, pos + 2, '{', '}')
                    elif next_ == '[':
                        endpos, more_substitutions = self._find_brackets_end(
                            data, pos + 2, '[', ']')

                    inner_data = data[(pos + 2):(endpos - 1)]
                    if more_substitutions:
                        inner_data = self.substitute_variables(
                            inner_data, where)

                    if next_ == '{':
                        inner_data = self._process_variable(
                            inner_data, where)
                    elif next_ == '[':
                        inner_data = self._process_expression(
                            inner_data, where)

                    ret.append(inner_data)
                    data = data[endpos:]
                    beginpos = searchpos = 0
                else:
                    searchpos = pos + 1

        return Variable.join(ret)

    def _find_brackets_end(self, data, pos, beginbracket, endbracket):
        more_substitutions = False
        brackets = 1
        while brackets:
            try:
                ch = data[pos]
            except IndexError:
                raise ParseError(
                    "Error in extension logic (missing '}')")  # TODO
            if ch == '$':
                if data[(pos + 1):(pos + 2)] in '{[':
                    more_substitutions = True
            elif ch == beginbracket:
                brackets += 1
            elif ch == endbracket:
                brackets -= 1
            pos += 1
        return pos, more_substitutions

    def _process_variable(self, data, where):
        if '(' in data:
            raise NotImplementedError(
                'FUNCTION support not implemented yet: {} (at {})'.format(
                    data, where))
        if ':' in data:
            raise NotImplementedError(
                'SUBSTRING support not implemented yet: {} (at {})'.format(
                    data, where))

        # If data is a variable already, there's not much more we can do.
        if not isinstance(data, Variable):
            assert all((i in string.ascii_letters or
                        i in string.digits or
                        i == '_')
                       for i in data), data
            self._variables[data].append(where)

        # On to return something sensible.
        return Variable(data)

    def _process_expression(self, data, where):
        raise NotImplementedError(
            'EXPR support not implemented yet: {} (at {})'.format(
                data, where))


class AppLoader(metaclass=Singleton):
    def __init__(self, version='v11'):
        self.version = version
        self._lower_apps = {}
        self._used_apps = set()

        self.load_all()

    @property
    def used_apps(self):
        return list(sorted(
            (i for i in self._lower_apps.values() if i.name != 'Unknown'),
            key=(lambda x: x.name)))

    @property
    def used_modules(self):
        return list(filter(
            (lambda x: x != 'unknown'),
            sorted(set(
                [self._lower_apps[i].module
                 for i in self._used_apps]))))

    def load_all(self):
        # Load all from our version dir.
        appsdir = os.path.join(os.path.dirname(__file__),
                               'app', self.version)
        appsmods = [i[0:-3] for i in os.listdir(appsdir) if i.endswith('.py')]

        for appsmod in appsmods:
            mod_name = 'asterisklint.app.{}.{}'.format(self.version, appsmod)
            mod = import_module(mod_name)
            if hasattr(mod, 'register'):
                mod.register(self)

    def get(self, lower_app):
        # Fetch app named lower_app. If it doesn't exist, we alias the
        # 'Unknown' app to it.
        if lower_app not in self._lower_apps:
            # TODO: at this point we want an error raised here, right?
            self._lower_apps[lower_app] = self._lower_apps['unknown']

        self._used_apps.add(lower_app)
        return self._lower_apps[lower_app]

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
        self.data = self.parse_inner(self.data)

        # Check app availability.
        if app.name != self.app:
            if app.name == 'Unknown':
                E_APP_MISSING(self.where, app=self.app)
            else:
                W_APP_BAD_CASE(self.where, app=self.app, proper=app.name)

        # Run data through app.
        app(self.data, where=self.where)

    def parse_inner(self, data):
        """
        Asterisk calls pbx_substitute_variables_helper_full on the
        entire app "data" line. So do we.

        SOURCE: main/pbx.c: pbx_extension_helper, calls
        SOURCE: main/pbx.c: pbx_substitute_variables_helper_full.
        """
        if '${' in data or '$[' in data:
            try:
                data = VarsLoader().substitute_variables(data, self.where)
            except NotImplementedError:  # FIXME: remove this
                pass
            except ParseError:
                E_APP_PARSE_ERROR(self.where, app=self.app, args=data)
        return data

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
            W_APP_NEED_PARENS(self.where, app=app)

        # Set it and try to find a handler for it.
        self.app = app
        self.app_lower = app.lower()
        self.data = data

        # Leading whitespace is frowned upon but allowed. Trailing
        # whitespace won't work:
        if self.app.rstrip() != self.app:
            E_APP_WSH(self.where, app=self.app)
            return False
        if self.app.lstrip() != self.app:
            W_APP_WSH(self.where, app=self.app)
            self.app = self.app.lstrip()
            self.app_lower = self.app.lower()
        # Quick check that the app doesn't exist.
        if not self.app:
            E_APP_MISSING(self.where, app='(none)')
            return False

        return True

    @property
    def name(self):
        return self.app
