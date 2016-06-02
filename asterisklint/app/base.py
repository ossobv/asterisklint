# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2016  Walter Doekes, OSSO B.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from ..application import W_APP_BALANCE
from ..defines import ErrorDef
from ..variable import Var, strjoin


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

    class E_APP_ARG_IFCONST(ErrorDef):
        message = ("apparent constant in If-condition; app {app!r}, "
                   "data '{data}' and cond '{cond}'")

    class E_APP_ARG_IFEMPTY(ErrorDef):
        message = "empty If-condition; app {app!r}, data '{data}'"

    class E_APP_ARG_IFSTYLE(ErrorDef):
        message = ("{app!r} takes the form <cond>?<iftrue>[:<iffalse>] "
                   "but data is '{data}', cond '{cond}', args '''{args}'''")

    class E_APP_ARG_PIPEDELIM(ErrorDef):
        message = ('the application delimiter is now the comma, not '
                   'the pipe; see app {app!r} and data {data!r}')

    class E_APP_ARG_SYNTAX(ErrorDef):
        message = ('generic application syntax error; app {app!r} and '
                   'data {data!r}')


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
        str_options = [i for i in arg if isinstance(i, str)]
        bad_options = [i for i in str_options if i not in self.options]
        if bad_options:
            E_APP_ARG_BADOPT(where, argno=self.argno, app=self.app,
                             opts=''.join(bad_options))
        if len(str_options) != len(set(str_options)):
            E_APP_ARG_DUPEOPT(where, argno=self.argno, app=self.app,
                              opts=arg)


class AppBase(object):
    @property
    def name(self):
        return self.__class__.__name__

    @property
    def module(self):
        return self.__module__.rsplit('.', 1)[-1]

    def __call__(self, data, where, jump_destinations):
        """
        Subclasses may implement something that populates
        jump_destinations.
        """
        try:
            self.check_balance(data)
        except ValueError:
            W_APP_BALANCE(where, data=str(data))

    @staticmethod
    def check_balance(data):
        """
        This function is a simple check that looks sane, but is not
        implemented like this in Asterisk. It may warn you of badly
        placed delimiters, but you shouldn't use this to interpret
        variables.

        For that, see separate_args which is modeled after the function
        as implemented in Asterisk.
        """
        arr = ['X']
        for char in data:
            if isinstance(char, Var):
                # It's possible that we're looping over a Var variable.
                # In that case we'll have to assume the Var itself
                # contains no separators that we might be interested in.
                # E.g. we expect you do *not* do this:
                # ``Set(var=mailbox@context,s)``
                # ``VoiceMail(${var})``
                # But we expect you to do this:
                # ``Set(mailbox=mailbox@context)``
                # ``VoiceMail(${mailbox},s)``
                pass  # skip char
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
        # #define AST_STANDARD_APP_ARGS(...) => separate_args(',', True)
        # #define AST_STANDARD_RAW_ARGS(...) => separate_args(',', False)
        # SOURCE: main/app.c -- __ast_app_separate_args()
        #
        # TODO: we should separate args using a more sensible approach as
        # well, so we can warn on inconsistencies.
        brackets = 0
        parens = 0
        quotes = False
        skipnext = False

        ret = [[]]
        start = 0
        for i, char in enumerate(data):
            if isinstance(char, Var):
                # It's possible that we're looping over a Var variable.
                # In that case we'll have to assume the Var itself
                # contains no separators that we might be interested in.
                # E.g. we expect you do *not* do this:
                # ``Set(var=mailbox@context,s)``
                # ``VoiceMail(${var})``
                # But we expect you to do this:
                # ``Set(mailbox=mailbox@context)``
                # ``VoiceMail(${mailbox},s)``
                # Skip it?
                # #ret[-1].extend(data[start:i])  # skip char
                # #start = i + 1
                # Don't skip it, we want the returned value.
                pass
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
        squashed = []
        for letters in ret:
            letters = list(strjoin(letters))  # join sequences of strings
            if len(letters) == 1:
                squashed.append(letters[0])
            else:
                squashed.append(Var.join(letters))

        return squashed


class DelimitedArgsMixin(object):
    def __init__(self, arg_delimiter=',', arg_raw=False, **kwargs):
        self._arg_delimiter = arg_delimiter
        self._arg_raw = arg_raw

    def split_args(self, data, where):
        return self.separate_args(
            data, delimiter=self._arg_delimiter,
            remove_quotes_backslashes=self._arg_raw)

    def __call__(self, data, where, jump_destinations):
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
        assert args, 'AppArgsMixin wants some args for {!r}'.format(
            self.__class__.__name__)

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


class NoPipeDelimiterMixin(object):
    # TODO: we should not use this for the System() app,
    # nor for the SHELL() function,
    # and it would be improved if we checked for surrounding quotes
    # which clearly show that the user isn't doing anything unintended.

    def split_args(self, data, where):
        args = super().split_args(data, where)
        if len(args) == 1 and '|' in args[0]:
            E_APP_ARG_PIPEDELIM(where, app=self.name, data=data)

        return args


class App(NoPipeDelimiterMixin, AppArgsMixin, DelimitedArgsMixin, AppBase):
    """
    The App takes an optional args=[AppArg(...), ...] and max_args=INT,
    and checks the values if available.
    """
    pass


class IfStyleApp(DelimitedArgsMixin, AppBase):
    """
    The IfStyleApp takes the form <cond>?<iftrue>:<iffalse>.
    """
    def __init__(self, **kwargs):
        super().__init__(arg_delimiter='?', arg_raw=True, **kwargs)

    def split_args(self, data, where):
        args = super().split_args(data, where)

        if len(args) >= 2:
            if len(args) > 2:
                # This is no good either, with too many results.
                E_APP_ARG_MANY(where, app=self.name, data=data, max_args=2)

            # BEWARE: GosubIf and ExecIf use this method, while GotoIf
            # uses a simpler split. In the majority of cases the result
            # would be the same (barring crazy backslash usage).
            cond = args[0]
            actions = self.separate_args(
                args[1], delimiter=':', remove_quotes_backslashes=False)
            if len(actions) == 1:
                iftrue, iffalse = actions[0], None
            else:
                # We simply drop excess args here.
                assert len(actions) >= 2, actions
                iftrue, iffalse = actions[0], actions[1]

        else:
            assert len(args) == 1, args

            # Attempt to separate the arguments the old fashioned way.
            args = self.separate_args(
                data, ',', remove_quotes_backslashes=False)
            cond = args[0]
            iftrue = args[1:]
            if len(iftrue):
                E_APP_ARG_IFSTYLE(where, app=self.name, data=data,
                                  cond=args[0], args=args[1:])
            else:
                E_APP_ARG_FEW(where, app=self.name, data=data, min_args=2)

            # Observe that iftrue is already split this time.
            cond, iftrue, iffalse = args[0], args[1:], None

        # Trim space from the sides of cond.
        cond = cond.strip()
        if cond == '':
            E_APP_ARG_IFEMPTY(where, app=self.name, data=data)

        return cond, iftrue, iffalse


class VarCondIfStyleApp(IfStyleApp):
    """
    Like IfStyleApp it takes the form <cond>?<iftrue>:<iffalse>, but
    the condition cannot contain constants.

    Use this for GotoIf/ExecIf.
    """
    def split_args(self, data, where):
        cond, iftrue, iffalse = super().split_args(data, where)

        # Check whether cond is a constant.
        if (cond != '' and  # already checked with E_APP_ARG_IFEMPTY
                (isinstance(cond, str) or
                 any(isinstance(i, str) for i in cond))):
            # NOTE: The resultant value is parsed with sscanf, and the
            # remainder is discarded. For example, something that
            # evaluates to "1&0" is parsed as "1" => "$[1=1]&$[0=0]"
            # (which should have been written as "$[1=1&0=0]") would
            # evaluate to True.
            E_APP_ARG_IFCONST(where, app=self.name, data=data,
                              cond=cond)

        return cond, iftrue, iffalse
