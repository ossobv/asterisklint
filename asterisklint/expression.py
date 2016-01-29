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
from .variable import Var


class Expr(Var):
    """
    A special case of Var where an expression is evaluated.

    TODO: complain about (expr);
    - excess whitespace
    - no agreement on quotes on either side of expression
    - bad/unknown operators
    - joined expressions (expr in expr, which is not needed, because you
      can use parens)
    """
    def __init__(self, expression=None):  # drop start and length args
        super().__init__(name=expression)

    def __str__(self):
        if self.name:
            return '$[{}]'.format(self.name)
        return super().__str__()
