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
