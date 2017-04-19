# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2017  Walter Doekes, OSSO B.V.
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
import re


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

            if not var:
                # Skip empty vars.
                pass
            elif copy and isinstance(var, str) and isinstance(copy[-1], str):
                # Join consecutive strings together.
                copy[-1] = copy[-1] + var
            else:
                # Append.
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

    def could_match(self, value):
        """
        Check if this variable could match the value passed if the
        circumstances (the inner variables) are right.

        Examples::

            Var('${number}23').could_match('123') == True
            Var('${user}@${domain}').could_match('somelabel') == False
        """
        if self.name:  # this is a plain variable, it could match anything
            return True

        re_joined = ''.join(
            ['^'] +
            [(re.escape(i) if isinstance(i, str) else '.*') for i in self] +
            ['$'])
        return re.match(re_joined, str(value))

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
        """
        Get an item or list of items.

        If a slice is requested (and a list is returned), we attempt to
        join the list using strjoin. Examples::

            ['A', 'B', 'C', <Var>, 'D'] ==> ['ABC', <Var>, 'D']
            ['A', 'B', 'C'] ==> 'ABC'
            ['A'] ==> 'A'
            [<Var>] ==> <Var>
            [] ==> []

        This should never be a problem because you'll be iterating over
        the results anyway.
        """
        item = self._get_cached_iter().__getitem__(*args, **kwargs)
        if isinstance(item, list):
            ret = list(strjoin(item))  # joins consecutive strings together
            if len(ret) == 1:
                return ret[0]
            return ret
        return item

    def __len__(self):
        return len(self._get_cached_iter())

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

    def split(self, token=':', maxsplit=-1):
        # In case we're an atom, pretend we're a list.
        if self.name:
            list_ = [self.name]  # [name]  # (start, length)
        else:
            list_ = self._list   # [contents...]  # (start, length)

        assert (
            (token == ':' and maxsplit == -1) or    # ${var:start:len}
            (token == '=' and maxsplit == 1) or     # Set(X=Y)
            (token == '(' and maxsplit == 1)        # FUNC(x)
        ), (token, maxsplit)  # unexpected split token..

        ret = self._split(list_, token, maxsplit)
        return ret

    def _split(self, source, token, maxsplit):
        # Split it up by token, so we group the values into subgroups.
        split_up = [[]]
        maxsplit_done = 0

        for item in source:
            if not isinstance(item, str):
                split_up[-1].append(item)
            elif token not in item or (maxsplit == maxsplit_done):
                split_up[-1].append(item)
            else:
                if maxsplit == -1:
                    subitems = item.split(token, maxsplit)
                else:
                    subitems = item.split(token, maxsplit - maxsplit_done)

                while len(subitems) > 1:
                    first = subitems.pop(0)
                    if first:
                        split_up[-1].append(first)
                    split_up.append([])
                    maxsplit_done += 1

                if subitems[0]:
                    split_up[-1].append(subitems[0])

        # Join the subgroups back into variables.
        for i, list_ in enumerate(split_up):
            if len(list_) == 0:
                split_up[i] = ''
            elif len(list_) > 1:
                split_up[i] = Var.join(split_up[i])
            else:
                split_up[i] = split_up[i][0]

        return split_up

    def strip(self):
        if self.name:
            return self  # no (deep)copy?

        new_list = self._list[:]
        if isinstance(new_list[0], str) and new_list[0].strip() == '':
            new_list = new_list[1:]
        if (new_list and isinstance(new_list[-1], str) and
                new_list[-1].strip() == ''):
            new_list = new_list[0:-1]

        if len(new_list) == len(self._list):
            return self  # no (deep)copy?
        if len(new_list) == 1:
            return new_list[0]

        v = Var()
        v._list = new_list  # no deepcopy..
        return v


class SliceMixin(object):
    def __init__(self, *args, start=None, length=None, **kwargs):
        assert start is not None
        super().__init__(*args, **kwargs)
        self.start = start
        self.length = length
        if length is not None:
            assert length != 0
            if length < 0:
                self._endpos = length
            elif self.start < 0:
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


class VarSlice(SliceMixin, Var):
    def __init__(self, name=None, start=None, length=None):
        assert name is not None
        super().__init__(name=name, start=start, length=length)


class VarDynSlice(Var):
    def __init__(self, name=None, start=None, length=None):
        assert name is not None
        super().__init__(name=name)
        self.start = start
        self.length = length

    def __str__(self):
        if self.length:
            return '${{{}:{}:{}}}'.format(
                self.name, self.start, self.length)
        return '${{{}:{}}}'.format(
            self.name, self.start)


def strjoin(list_of_items_and_strings):
    """
    Joins all consecutive items that are strings together.

    E.g.: [1, 2, 'a', 'b', 'c', 3, 'd', 'e'] ==> [1, 2, 'abc', 3, 'de']
    """
    cache = []
    for ch in list_of_items_and_strings:
        if isinstance(ch, str):
            cache.append(ch)
        else:
            if cache:
                yield ''.join(cache)
                cache = []
            yield ch
    if cache:
        yield ''.join(cache)


def variable_check_balance(data):
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
            # Same goes for functions.
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
