import string
from collections import defaultdict

from .cls import Singleton


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
        if '(' in data:
            raise NotImplementedError(
                'FUNCTION support not implemented yet: {} (at {})'.format(
                    data, where))
        if ':' in data:
            raise NotImplementedError(
                'SUBSTRING support not implemented yet: {} (at {})'.format(
                    data, where))

        # If data is a variable already, there's not much more we can do.
        if not isinstance(data, Var):
            assert all((i in string.ascii_letters or
                        i in string.digits or
                        i == '_')
                       for i in data), data
            self._variables[data].append(where)

        # On to return something sensible.
        return Var(data)

    def _process_expression(self, data, where):
        raise NotImplementedError(
            'EXPR support not implemented yet: {} (at {})'.format(
                data, where))
