from ..application import W_APP_BALANCE, Variable
from ..defines import ErrorDef


# TODO: instead of where, we should pass a context object that context
# could include a where, and also a list of classes where we can store
# significant info like "label" when there is a goto/gosub that jumps to
# one.


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_APP_ARG_FEW(ErrorDef):
        message = 'too few arguments for app {app!r}, minimum is {min_args}'

    class E_APP_ARG_MANY(ErrorDef):
        message = 'too many arguments for app {app!r}, maximum is {max_args}'

    class E_APP_ARG_BADOPT(ErrorDef):
        message = ('unrecognised options {opts!r} in arg {argno} '
                   'for app {app!r}')

    class E_APP_ARG_DUPEOPT(ErrorDef):
        message = 'duplicate options {opts!r} in arg {argno} for app {app!r}'


class AppArg(object):
    def __init__(self, name):
        self.name = name
        # The following are set afterwards.
        self.argno = None
        self.app = None

    def validate(self, arg, where):
        pass


class AppOptions(AppArg):
    def __init__(self, options):
        super().__init__('options')
        self.options = options

    def validate(self, arg, where):
        bad_options = [i for i in arg if i not in self.options]
        if bad_options:
            E_APP_ARG_BADOPT(where, argno=self.argno, app=self.app,
                             opts=''.join(bad_options))
        if len(arg) != len(set(arg)):
            E_APP_ARG_DUPEOPT(where, argno=self.argno, app=self.app,
                              opts=arg)


class AppBase(object):
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def module(self):
        return self.__module__.rsplit('.', 1)[-1]

    def __call__(self, data, where):
        try:
            self.check_balance(data)
        except ValueError:
            W_APP_BALANCE(where, data=data)

    @staticmethod
    def check_balance(data):
        # TODO: we don't check backslash escapes here, should we?
        # TODO: write proper tests for this?

        arr = ['X']
        for char in data:
            if isinstance(char, Variable):
                pass
            elif char == '"':
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

    @staticmethod
    def separate_args(data, delimiter=',', remove_quotes_backslashes=True):
        """
        #define AST_STANDARD_APP_ARGS(...) => separate_args(',', True)
        #define AST_STANDARD_RAW_ARGS(...) => separate_args(',', False)

        SOURCE: main/app.c -- __ast_app_separate_args()

        TODO: we should separate args using a more sensible approach as
        well, so we can warn on inconsistencies.
        """
        brackets = 0
        parens = 0
        quotes = False
        skipnext = False

        ret = [[]]
        start = 0
        for i, char in enumerate(data):
            if isinstance(char, Variable):
                # Skip.
                ret[-1].extend(data[start:i])
                start = i + 1
            elif skipnext:
                skipnext = False
            elif char == '[':
                brackets += 1
            elif char == ']':
                if brackets:
                    brackets -= 1
            elif char == '(':
                parens += 1
            elif char == ')':
                if parens:
                    parens -= 1
            elif char == '"' and delimiter != '"':
                quotes = not quotes
                if remove_quotes_backslashes:
                    ret[-1].extend(data[start:i])
                    start = i + 1
            elif char == '\\':
                if remove_quotes_backslashes:
                    ret[-1].extend(data[start:i])
                    start = i + 1
                skipnext = True
            elif char == delimiter and not (brackets or parens or quotes):
                ret[-1].extend(data[start:i])
                start = i + 1
                ret.append([])  # start on next arg

        # Append leftover args.
        ret[-1].extend(data[start:])

        # Squash args.
        ret = [''.join(i) for i in ret]

        return ret


class DelimitedArgsMixin(object):
    def __init__(self, arg_delimiter=',', arg_raw=False, **kwargs):
        self._arg_delimiter = arg_delimiter
        self._arg_raw = arg_raw

    def split_args(self, data, where):
        return self.separate_args(
            data, delimiter=self._arg_delimiter,
            remove_quotes_backslashes=self._arg_raw)

    def __call__(self, data, where):
        return self.split_args(data, where)


class MinMaxArgsMixin(object):
    def __init__(self, min_args=None, max_args=None, **kwargs):
        super().__init__(**kwargs)
        assert (min_args is None or max_args is None or
                min_args <= max_args)
        self._min_args = min_args
        self._max_args = max_args

    def split_args(self, data, where):
        args = super().split_args(data, where)

        if self._min_args is not None and (
                (len(args) < self._min_args) or
                (self._min_args == 1 and len(args) == 1 and not args[0])):
            E_APP_ARG_FEW(where, app=self.name, min_args=self._min_args)
        elif self._max_args is not None and (
                (len(args) > self._max_args)):
            E_APP_ARG_MANY(where, app=self.name, max_args=self._max_args)

        return args


class AppArgsMixin(MinMaxArgsMixin):
    def __init__(self, args=None, **kwargs):
        assert args
        super().__init__(max_args=len(args), **kwargs)

        # Set the arguments and pimp them a bit with more info.
        self._args = args
        for i, arg in enumerate(self._args):
            arg.argno = i + 1
            arg.app = self.name

    def split_args(self, data, where):
        args = super().split_args(data, where)

        for i, arg in enumerate(args):
            if len(self._args) > i:
                self._args[i].validate(arg, where)

        return args


class App(AppArgsMixin, MinMaxArgsMixin, DelimitedArgsMixin, AppBase):
    pass
