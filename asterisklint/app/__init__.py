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
from ..defines import ErrorDef, WarningDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_APP_ARG_FEW(ErrorDef):
        message = 'too few arguments for app {app!r}, minimum is {min_args}'

    class E_APP_ARG_MANY(ErrorDef):
        message = 'too many arguments for app {app!r}, maximum is {max_args}'

    class E_APP_ARG_BADOPT(ErrorDef):
        message = ('unrecognised options {opts!r} in arg {argno} '
                   'for app {app!r}')

    class E_APP_ARG_DUPEOPT(ErrorDef):
        message = 'duplicate options {opts!r} in arg {argno} for app {app!r}'

    class E_APP_ARG_IFCONST(ErrorDef):
        message = ("apparent constant in If-condition; app {app!r}, "
                   "data '{data}' and cond '{cond}'")

    class E_APP_ARG_IFEMPTY(ErrorDef):
        message = "empty If-condition; app {app!r}, data '{data}'"

    class E_APP_ARG_IFSTYLE(ErrorDef):
        message = ("{app!r} takes the form <cond>?<iftrue>[:<iffalse>] "
                   "but data is '{data}', cond '{cond}', args '''{args}'''")

    class E_APP_ARG_PIPEDELIM(ErrorDef):
        message = ('the application delimiter is now the comma, not '
                   'the pipe; see app {app!r} and data {data!r}')

    class E_APP_ARG_SYNTAX(ErrorDef):
        message = ('generic application syntax error; app {app!r} and '
                   'data {data!r}')

    class E_APP_MISSING(ErrorDef):
        message = 'app {app!r} does not exist, dialplan will halt here!'

    class W_APP_BAD_CASE(WarningDef):
        message = 'app {app!r} does not have the proper Case {proper!r}'

    class W_APP_BALANCE(WarningDef):
        message = ('app data {data!r} looks like unbalanced '
                   'parentheses/quotes/curlies')
