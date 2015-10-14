import string
from collections import defaultdict

from .cls import Singleton
from .defines import ErrorDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_VAR_SUBSTR_ARGS(ErrorDef):
        message = "bad substring syntax of variable '{data}'"

    class E_VAR_SUBSTR_START(ErrorDef):
        message = "bad substring start value '{start}'"

    class E_VAR_SUBSTR_LENGTH(ErrorDef):
        message = "bad substring length value '{length}'"


class VarParseError(ValueError):
    pass


class Var(object):
    """
    Var is a nested structure of variables.

    For example::

        "${abc}"    => Var('abc')
        "abc${def}" => Var.join(['abc', Var('abc')])
        "${${abc}}" => Var(Var('abc'))
        "${a${bc}}" => Var(Var.join(['a', Var('bc')]))

    You can call stringify the Var back to their original values::

        str(Var('abc')) => "${abc}"
        ...

    You can also format the Var with variable replacements:

        Var(Var.join(['a', Var('bc')])).format(bc='BC', aBC='foobar') =>
          "foobar"
    """
    @classmethod
    def join(self, variables):
        copy = []
        for var in variables:
            if not isinstance(var, (str, Var)):
                raise TypeError(
                    'Variables can only consist of strings and other '
                    'variables, got {!r}'.format(var))
            if var:
                copy.append(var)

        if len(copy) == 0:
            return ''
        if len(copy) == 1:
            return copy[0]

        # Use private setter instead of constructor.
        ret = Var()
        ret._list = copy
        return ret

    def __init__(self, name=None, start=None, length=None):
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

        elif isinstance(self.name, Var):
            ret = self.name.format(**kwargs)
            return kwargs[ret]

        else:
            return kwargs[self.name]

    def __iter__(self):
        """
        You may iterate over this thing, as if it where a string. In
        which case you get the literal letters, and variables in
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
        if not isinstance(other, Var):
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


class VarSlice(Var):
    def __init__(self, name=None, start=None, length=None):
        assert name is not None and start is not None
        super().__init__(name=name)
        self.start = start
        self.length = length
        if length is not None:
            assert length != 0
            if self.start < 0:
                self._endpos = self.start + length
                assert self._endpos < 0
            else:
                self._endpos = self.start + length

    def format(self, **kwargs):
        value = super().format(**kwargs)
        if self.length:
            return value[self.start:self._endpos]
        return value[self.start:]

    def __str__(self):
        if self.length:
            return '${{{}:{}:{}}}'.format(
                self.name, self.start, self.length)
        return '${{{}:{}}}'.format(
            self.name, self.start)


class Expr(Var):
    """
    A special case of Var where an expression is evaluated.

    TODO: complain about (expr);
    - excess whitespace
    - no agreement on quotes on either side of expression
    - bad/unknown operators
    """
    def __init__(self, expression=None):  # drop start and length args
        super().__init__(name=expression)

    def __str__(self):
        if self.name:
            return '$[{}]'.format(self.name)
        return super().__str__()


class Func(Var):
    """
    A special case of Var where a function call is evaluated.

    TODO: this shouldn't be here probably, since we need the more
    complicated function loaders from elsewhere..
    """
    def __init__(self, func_and_args=None):
        super().__init__(name=func_and_args)


class VarLoader(metaclass=Singleton):
    """
    The VarLoader loads variables, functions and expressions. It's
    contained here with the variables only, because the functions are
    a special form of variables in asterisk.
    """
    def __init__(self, version='v11'):
        self.version = version
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
            return self._process_function(data, where)

        elif ':' in data:
            # Create sliced var and return.
            return self._process_variable_slice(data, where)

        else:
            # On to return something sensible.
            if not isinstance(data, Var):
                self._count_var(data, where)
            return Var(data)

    def _process_variable_slice(self, data, where):
        """
        Process: <varname>:<start>[:<length>]
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
            if (start and (start.isdigit() or
                           (start[0] == '-' and start[1:].isdigit()))):
                start = int(start)
            else:
                start = length = None
                E_VAR_SUBSTR_START(where, start=start)

        if length is not None:
            if length and length.isdigit():
                length = int(length)
                # If we use an offset from the end, then it makes no
                # sense to have a length that's as large or larger.
                if length == 0 or (start < 0 and -length <= start):
                    length = None
                    E_VAR_SUBSTR_LENGTH(where, length=length)
            else:
                start = length = None
                E_VAR_SUBSTR_LENGTH(where, length=length)

        # If start is 0 and there is no length, it makes no sense.
        if start == 0 and not length:
            start = None
            E_VAR_SUBSTR_START(where, start=start)

        # On to return something sensible.
        if not isinstance(varname, Var):
            self._count_var(varname, where)

        if start is None:
            return Var(varname)
        return VarSlice(varname, start=start, length=length)

    def _process_expression(self, data, where):
        """
        Process: <expression>
        """
        # We should parse the expression and supply errors/warnings
        # here, before returning the expression.
        return Expr(data)

    def _process_function(self, data, where):
        """
        Process: <function>(<args>)
        """
        # We should do actual function parsing stuff...
        return Func(data)

    def _count_var(self, varname, where):
        assert isinstance(varname, str), varname
        assert all((i in string.ascii_letters or
                    i in string.digits or
                    i == '_')
                   for i in varname), varname
        self._variables[varname].append(where)
