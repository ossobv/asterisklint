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
import string
from collections import defaultdict
from importlib import import_module

from .cls import Singleton
from .defines import ErrorDef, WarningDef
from .expression import Expr
from .function import ReadFunc, ReadFuncSlice
from .variable import Var, VarSlice, VarDynSlice
from .version import AsteriskVersion


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_FUNC_BAD_CASE(ErrorDef):
        message = 'function {func!r} does not have the proper Case {proper!r}'

    class E_FUNC_MISSING(ErrorDef):
        # BUG: this is also called for func_odbc created functions..
        message = 'function {func!r} does not exist (or func_odbc created?)'

    class E_FUNC_PARENS(ErrorDef):
        message = "missing trailing parenthesis for function call '{data}'"

    class E_FUNC_TAIL(ErrorDef):
        message = "excess tokens at the end of the function call '{data}'"

    class E_VAR_SUBSTR_ARGS(ErrorDef):
        message = "bad substring syntax of variable '{data}'"

    class E_VAR_SUBSTR_START(ErrorDef):
        message = "bad substring start value '{start}'"

    class E_VAR_SUBSTR_LENGTH(ErrorDef):
        message = "bad substring length value '{length}'"

    class W_FUNC_DYNAMIC(WarningDef):
        message = "calling functions dynamically is not good practise '{data}'"


class VarParseError(ValueError):
    pass


class FuncLoader(metaclass=Singleton):
    """
    The FuncLoader loads functions. It is called by the VarLoader when a
    function is encountered.
    """
    def __init__(self):
        self._lower_funcs = defaultdict(list)
        self._used_funcs = set()

        self.load_all()

    @property
    def used_funcs(self):
        return list(
            self._lower_funcs[i]
            for i in sorted(self._used_funcs)
            if i != 'unknown')

    @property
    def used_modules(self):
        return list(filter(
            (lambda x: x != 'unknown'),
            sorted(set(
                [self._lower_funcs[i].module
                 for i in self._used_funcs]))))

    def load_all(self):
        for mod_name in AsteriskVersion().list_func_mods():
            mod = import_module(mod_name)
            if hasattr(mod, 'register'):
                mod.register(self)

    def get(self, lower_func):
        # Fetch func named lower_func. If it doesn't exist, we alias the
        # 'UNKNOWN' func to it.
        if lower_func not in self._lower_funcs:
            if 'unknown' not in self._lower_funcs:
                raise NotImplementedError(
                    'There should be an UNKNOWN function that we can map '
                    'unknown functions to!')
            # We don't raise anything here, we do that outside, when we
            # see that the appname is not canonical.
            self._lower_funcs[lower_func] = self._lower_funcs['unknown']

        self._used_funcs.add(lower_func)
        return self._lower_funcs[lower_func]

    def register(self, func):
        lower_func = func.name.lower()
        self._lower_funcs[lower_func] = func

    def process_function(self, func_and_args, where):
        """
        Process: <function>(<args>)
        """
        # SOURCE: main/pbx.c -- ast_func_read2, func_args
        for i, char in enumerate(func_and_args):
            if char == '(':
                func = func_and_args[0:i]
                break
        assert func  # we only get here if there is a '('

        # Search backwards for the trailing ')'.
        tail = ''
        for n in range(len(func_and_args) - 1, i, -1):
            if func_and_args[n] == ')':
                args = func_and_args[(i + 1):n]
                tail = func_and_args[n + 1:]
                break
        else:
            # "Can't find trailing parenthesis for function"
            E_FUNC_PARENS(where, data=func_and_args)
            args = func_and_args[(i + 1):]

        # Do we have a tail of ":<offset>:<length>"? Process it:
        if tail:
            varname, start, length = VarLoader().split_variable_slice(
                tail, where)

            if varname:
                start = length = None
                E_FUNC_TAIL(where, data=func_and_args)
        else:
            start = length = None

        # func should be a regular string. If it isn't, you're doing
        # crazy stuff like: ${funcname}(${args})
        # I will complain.
        if isinstance(func, Var):
            # We won't be able to match any real functions. And you
            # should get a big fat warning.
            W_FUNC_DYNAMIC(where, func=func)

            if start is not None:
                return ReadFuncSlice(func, args, start=start, length=length)
            return ReadFunc(func, args)

        # Okay, so we have a string function. Look it up.
        loaded = FuncLoader().get(func.lower())

        # Check function availability.
        if loaded.name != func:
            if loaded.name == 'UNKNOWN':
                E_FUNC_MISSING(where, func=func)
            else:
                E_FUNC_BAD_CASE(where, func=func, proper=loaded.name)

        # TODO: do more stuff with this..?

        if start is not None:
            return ReadFuncSlice(func, args, start=start, length=length)
        return ReadFunc(func, args)


class VarLoader(metaclass=Singleton):
    """
    The VarLoader loads variables, functions and expressions. It's
    contained here with the variables only, because the functions are
    a special form of variables in asterisk.
    """
    def __init__(self):
        self._variables = defaultdict(list)

    def parse_variables(self, data, where):
        """
        Parse variables will loop over the data and extract all
        variables. This function mimic the behaviour of Asterisk
        variable substitution, except we don't do the substitution just
        yet. (Because we don't know the values of the variables.)
        """
        # SOURCE: main/pbx.c -- ast_str_substitute_variables_full
        # SOURCE: main/pbx.c -- pbx_substitute_variables_full
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
                        inner_data = self.parse_variables(
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

        return Var.join(ret)

    def _find_brackets_end(self, data, pos, beginbracket, endbracket):
        more_substitutions = False
        brackets = 1
        while brackets:
            try:
                ch = data[pos]
            except IndexError:
                raise VarParseError(
                    'Error in extension logic (missing {!r})'.format(
                        endbracket))
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
        """
        Process: <varname>

        (Or sliced variable, or expression, or function.)
        """
        if '(' in data:
            # Create function and return.
            return FuncLoader().process_function(data, where)

        elif ':' in data:
            # Create sliced var and return.
            return self._process_variable_slice(data, where)

        else:
            # Count Var usage.
            if not isinstance(data, Var):
                self.count_var(data, where)

            # On to return something sensible.
            return Var(data)

    def _process_variable_slice(self, data, where):
        """
        Process: <varname>:<start>[:<length>]
        """
        varname, start, length = self.split_variable_slice(data, where)

        # Count Var usage.
        if not isinstance(varname, Var):
            self.count_var(varname, where)

        # On to return something sensible.
        if start is None:
            return Var(varname)

        # Very dynamic, this..
        if isinstance(start, Var) or isinstance(length, Var):
            return VarDynSlice(varname, start=start, length=length)

        return VarSlice(varname, start=start, length=length)

    def _process_expression(self, data, where):
        """
        Process: <expression>
        """
        # We should parse the expression and supply errors/warnings
        # here, before returning the expression.
        return Expr(data)

    def count_var(self, varname, where):
        assert isinstance(varname, str), varname
        assert all((i in string.ascii_letters or
                    i in string.digits or
                    i == '_')
                   for i in varname), varname
        self._variables[varname].append(where)

    @staticmethod
    def split_variable_slice(data, where):
        """
        Split up: <varname>:<start>[:<length>] and return the three
        parts.
        """
        parts = data.split(':')
        if len(parts) == 2:
            varname, start, length = parts[0], parts[1], None
        elif len(parts) == 3:
            varname, start, length = parts[0], parts[1], parts[2]
        else:
            varname = parts[0]
            start = length = None
            E_VAR_SUBSTR_ARGS(where, data=data)

        if start is not None:
            if isinstance(start, Var):
                # We cannot determine anything more from this.
                pass
            elif (start and (
                    start.isdigit() or
                    (start[0] == '-' and start[1:].isdigit()))):
                start = int(start)
            else:
                start = length = None
                E_VAR_SUBSTR_START(where, start=start)

        if length is not None:
            if isinstance(length, Var):
                # We cannot determine anything more from this.
                pass
            elif (length and (
                    length.isdigit() or
                    (length[0] == '-' and length[1:].isdigit()))):
                length = int(length)
                # If we use an offset from the end, then it makes no
                # sense to have a length that's as large or larger.
                if length == 0 or (start < 0 and -length <= start):
                    length = None
                    E_VAR_SUBSTR_LENGTH(where, length=length)
            else:
                E_VAR_SUBSTR_LENGTH(where, length=length)
                start = length = None

        # If start is 0 and there is no length, it makes no sense.
        if start == 0 and not length:
            start = None
            E_VAR_SUBSTR_START(where, start=start)

        return varname, start, length
