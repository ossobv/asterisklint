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
import re

from .config import (
    E_CONF_KEY_DUPE, E_CONF_KEY_INVALID, W_CONF_KEY_LATE,
    ConfigAggregator, Context)
from .defines import ErrorDef, WarningDef
from .func.base import FuncBase
from .varfun import FuncLoader


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_ODBC_NOSQL(ErrorDef):
        message = ('a readsql and/or writesql (and insertsql) statement is '
                   'required')

    class W_ODBC_BADTOKENS(WarningDef):
        message = ('odbc function {name!r} should be uppercase '
                   'with A-Z0-9_ only')

    class W_ODBC_LEGACY(WarningDef):
        message = ('read and write are legacy, use readsql and writesql '
                   '(and insertsql) instead')

    class W_ODBC_TAILSEMI(WarningDef):
        message = 'tailing semicolon is unnecessary'


class FuncOdbcFunc(FuncBase):
    @property
    def module(self):
        # This would be correct automatically, since this module is
        # called func_odbc, but it doesn't hurt to be explicit.
        return 'func_odbc'


class OdbcFunction(Context):
    ORDER = ('prefix', 'synopsis', 'dsn', 'escapecommas', 'mode', 'rowlimit',
             # 'insertsql' is used when the writesql update returned 0
             # updated rows.
             'readhandle', 'readsql', 'writehandle', 'writesql', 'insertsql',
             'read', 'write')  # legacy

    def get_name(self):
        return self.name

    def get_function_name(self):
        return '{}_{}'.format(self.get_prefix(), self.get_name())

    def get_prefix(self):
        return self.get_variable('prefix') or 'ODBC'

    def get_variable(self, variable):
        for var in self._varsets:
            if var.variable == variable:
                return var.value
        return None

    def has_variable(self, variable):
        return self.get_variable(variable) is not None

    def add(self, varset):
        if self.check_order(self._varsets, varset):

            # Check for trailing semicolons.
            if varset.variable in (
                    'readsql', 'writesql', 'insertsql', 'read', 'write'):
                if varset.variable in ('read', 'write'):
                    W_ODBC_LEGACY(varset.where)
                if varset.value.endswith(';'):
                    W_ODBC_TAILSEMI(varset.where)
            # TODO:
            # - check for usage/missing ARGn/VALn (only VALn in
            #   write/insert)
            # - properly formatted ${SQL_ESC(${ARG4})}
            # - prefix should be uppercase
            # - check SQL syntax?

            return super().add(varset)

    def update(self, context):
        raise NotImplementedError('when? how? what?')

    def check_order(self, set_, new):
        try:
            new_pos = self.ORDER.index(new.variable)
        except ValueError:
            E_CONF_KEY_INVALID(new.where, key=new.variable)
            return False

        if set_:
            used_poses = [self.ORDER.index(i.variable) for i in set_]
            if new_pos in used_poses:
                # func_odbc.c uses ast_variable_retrieve (checked on jan
                # 2016 in Asterisk 13), so it uses the first key, not
                # the last.
                previous = [i for i in set_ if i.variable == new.variable][0]
                E_CONF_KEY_DUPE(new.where, key=new.variable, previous=previous)
                return False

            if new_pos < used_poses[-1]:
                # We expected this key sooner.
                W_CONF_KEY_LATE(new.where, key=new.variable)

        return True

    def finalize(self):
        # TODO:
        # - Check that we have not both read and readsql (and friends)
        # - Check that there is a dsn or a *handle for every *sql.
        # - Check existence of synopsis/syntax
        # - Note: syntax=(empty) does not work, use syntax=void or
        #   syntax=arg1,arg2 (syntax check should match comma's to
        #   ARGn count)

        if not self.finalize_check_any_read_write():
            return
        self.finalize_register()

    def finalize_check_any_read_write(self):
        if not (self.has_variable('read') or self.has_variable('write') or
                self.has_variable('readsql') or self.has_variable('writesql')):
            E_ODBC_NOSQL(self.where)
            return False
        return True

    def finalize_register(self):
        # Register the custom function.
        odbc_function_class = type(
            self.get_function_name(), (FuncOdbcFunc,), {})
        FuncLoader().register(odbc_function_class())


class FuncOdbcAggregator(ConfigAggregator):
    """
    TODO: This should instead be split up into a simple config parser
    which also handles inheritance and a really short func_odbc
    aggregator.
    """
    # Allow A_B_C and ABC, but not _A or B_ or AB__C.
    FUNC_NAME_RE = re.compile(r'^[A-Z0-9](_?[A-Z0-9])*$')

    def on_yield(self):
        for function in super().on_yield():
            function.finalize()
            yield function

        # TODO: - Check for dupe functions/contexts.  jan2016 check in
        # pbx.c says that duplicate functions do not get registered =>
        # first one wins

    def on_context(self, context):
        if not self.FUNC_NAME_RE.match(context.name):
            W_ODBC_BADTOKENS(context.where, name=context.name)

        context = OdbcFunction.from_context(context)
        return super().on_context(context)

    def on_varset(self, varset):
        assert not varset.arrow  # W_ARROW
        return super().on_varset(varset)
