import string
from collections import defaultdict

from .cls import Singleton
from .defines import ErrorDef
from .expression import Expr
from .function import Func
from .variable import Var, VarSlice


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_VAR_SUBSTR_ARGS(ErrorDef):
        message = "bad substring syntax of variable '{data}'"

    class E_VAR_SUBSTR_START(ErrorDef):
        message = "bad substring start value '{start}'"

    class E_VAR_SUBSTR_LENGTH(ErrorDef):
        message = "bad substring length value '{length}'"


class VarParseError(ValueError):
    pass


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
