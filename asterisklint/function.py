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
from .variable import SliceMixin, Var


class ReadFunc(Var):
    """
    A special case of VarSlice where a function call is evaluated.

    The ReadFunc is different from the WriteFunc in that the ReadFunc
    has surrounding ${} tokens and allows slicing.
    """
    def __init__(self, func=None, args=None):
        assert func is not None and args is not None

        # The "convenience" strjoin in Var getslice creates trouble for
        # us here: args can be a list or a simple iterable.
        if isinstance(args, list):
            func_and_args = [func, '('] + args + [')']
        else:
            func_and_args = [func, '(', args, ')']

        super().__init__(name=Var.join(func_and_args))

        self.func = func
        self.args = args


class ReadFuncSlice(SliceMixin, ReadFunc):
    pass
