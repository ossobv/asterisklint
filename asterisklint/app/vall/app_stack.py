# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2020  Walter Doekes, OSSO B.V.
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
from ..base import (
    E_APP_ARG_MANY, W_APP_BALANCE,
    AppBase, DelimitedArgsMixin, MinMaxArgsMixin, NoPipeDelimiterMixin,
    VarCondIfStyleApp)
from ...variable import Var


class _GosubMixin:
    def _gosub_args_to_destination(self, args, where):
        # jumpdest = [[context,]exten,]prio(args)
        jumpdest = args[:]  # don't touch caller args

        if len(jumpdest) > 3:
            # See: ast_parseable_goto()
            # Priority '%s' must be a number > 0, or valid label.
            if not isinstance(self, MinMaxArgsMixin):
                # The MinMaxArgsMixin would already have warned.
                E_APP_ARG_MANY(where, app=self.name, max_args=3)

            # This should also raise a W_DP_GOTO_CONTEXT_NOEXTEN later on,
            # unless it contains vars and the warning is suppressed.
            # (Join the excess arguments with a comma separator.)
            excess = [jumpdest[2]]
            [excess.extend((',', i)) for i in jumpdest[3:]]
            jumpdest[2:] = [Var.join(excess)]
        while len(jumpdest) < 3:
            jumpdest.insert(0, None)
        assert len(jumpdest) == 3, jumpdest

        # Quickly drop the Gosub-args for now.
        # Only use the label (context+exten+prio).
        # (Technically, the args-split (parenthessis) is done in
        # app_stack.c before the label-split (comma). But that's of no
        # concern at the moment.)
        jumpdest[2] = self._split_gosub_prio_args(jumpdest[2], where)[0]
        return tuple(jumpdest)

    def _split_gosub_prio_args(self, prio, where):
        """
        Split off the (<args>) from from <prio>(<args>).
        """
        args = None
        for i, token in enumerate(prio):
            if token == '(':
                if prio[-1] != ')':
                    W_APP_BALANCE(where, data=prio)
                    args = prio[(i + 1):]
                else:
                    args = prio[(i + 1):-1]
                prio = prio[0:i]
                break

        # FYI: The args are parsed by Asterisk using AST_STANDARD_RAW_ARGS.
        return prio, args


class Gosub(NoPipeDelimiterMixin, MinMaxArgsMixin, DelimitedArgsMixin,
            AppBase, _GosubMixin):

    def __init__(self, **kwargs):
        super().__init__(min_args=1, max_args=3, **kwargs)

    def __call__(self, data, where, jump_destinations):
        args = super().__call__(data, where, jump_destinations)
        jump_destinations.append(
            self._gosub_args_to_destination(args, where))

        return args


class GosubIf(VarCondIfStyleApp, _GosubMixin):
    def __call__(self, data, where, jump_destinations):
        cond, iftrue, iffalse = super().__call__(
            data, where, jump_destinations)

        for args in (iftrue, iffalse):
            if args:
                jumpdest = self.separate_args(args)
                jump_destinations.append(
                    self._gosub_args_to_destination(jumpdest, where))

        return cond, iftrue, iffalse


class Return(AppBase):
    pass


class StackPop(AppBase):
    pass


def register(app_loader):
    for app in (
            Gosub, GosubIf, Return, StackPop):
        app_loader.register(app())
