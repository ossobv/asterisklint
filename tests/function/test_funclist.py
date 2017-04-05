# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2017  Walter Doekes, OSSO B.V.
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
from asterisklint.alinttest import (
    ALintTestCase, GenerateTestCases, expectedFailure)
from asterisklint.varfun import FuncLoader
from asterisklint.where import DUMMY_WHERE

RDWR_FUNCTION_LIST = (
    'ARRAY', 'CALLERID', 'CALLERPRES', 'CDR', 'CHANNEL',
    'CONNECTEDLINE', 'DB', 'DB_DELETE',
    'ENV', 'GLOBAL', 'GROUP', 'HASH', 'LOCAL',
    'MASTER_CHANNEL', 'REDIRECTING', 'SHARED', 'TIMEOUT',
    # )
    #
    # RDONLY_FUNCTION_LIST = (
    'CHANNELS', 'CSV_QUOTE', 'CURL', 'CURLOPT', 'CUT',
    'DB_EXISTS', 'DB_KEYS', 'DEC',
    'ENUMLOOKUP', 'ENUMQUERY', 'ENUMRESULT', 'EVAL', 'EXISTS',
    'FIELDNUM', 'FIELDQTY', 'FILE', 'FILE_COUNT_LINE', 'FILE_FORMAT',
    'FILTER', 'GROUP_COUNT', 'GROUP_LIST', 'GROUP_MATCH_COUNT',
    'HASHKEYS', 'IF', 'IFTIME', 'IMPORT', 'INC', 'ISNULL', 'KEYPADHASH',
    'LOCAL_PEEK',
    'LEN', 'LISTFILTER', 'MATH', 'MD5',
    'PASSTHRU', 'POP', 'QUOTE', 'RAND',
    'REGEX', 'REPLACE', 'SHELL', 'SHIFT', 'SORT',
    'STACK_PEEK', 'STAT', 'STRFTIME',
    'STRPTIME', 'STRREPLACE', 'TOLOWER', 'TOUPPER', 'TXTCIDNAME',
    'URIDECODE', 'URIENCODE',
    # Disabled from RDONLY_FUNCTION_LIST because of alt-syntax.
    # 'SET',
    # )
    #
    # WRONLY_FUNCTION_LIST = (
    'PUSH', 'UNSHIFT',
)

WRONLY_FUNCTION_LIST = RDONLY_FUNCTION_LIST = ()  # FIXME: see above


class FunctionListTestBase(ALintTestCase):
    def readfunc(self, function):
        FuncLoader().process_read_function(
            '{}(random_argument)'.format(function), where=DUMMY_WHERE)

    def writefunc(self, function):
        FuncLoader().process_write_function(
            '{}(random_argument)'.format(function), where=DUMMY_WHERE)


class ReadWriteFunctionListTest(
        FunctionListTestBase, metaclass=GenerateTestCases(
            '_test_readwrite', [(i,) for i in RDWR_FUNCTION_LIST])):
    "Test that a bunch of functions exist for reading/writing."

    def _test_readwrite(self, function):
        "Test that Function '{}' exists for read/write (generated test)."
        self.readfunc(function)
        self.assertLinted({})

        self.writefunc(function)
        self.assertLinted({})

    def test_FOO(self):
        "Test that Function 'FOO' *does* *not* exist at all."
        self.readfunc('FOO')
        self.assertLinted({'E_FUNC_MISSING': 1})

        self.writefunc('FOO')
        self.assertLinted({'E_FUNC_MISSING': 1})


class ReadOnlyFunctionListTest(
        FunctionListTestBase, metaclass=GenerateTestCases(
            '_test_readonly', [(i,) for i in RDONLY_FUNCTION_LIST])):
    "Test that a bunch of functions exist for reading only."

    def _test_readonly(self, function):
        "Test that Function '{}' exists for reading only (generated test)."
        self.readfunc(function)
        self.assertLinted({})

        self.writefunc(function)
        self.assertLinted({'E_FUNC_RDONLY': 1})

    @expectedFailure
    def test_POP(self):
        "Test that Function 'POP' exists for reading only."
        self._test_readonly('POP')

    def test_PUSH(self):
        "Test that Function 'PUSH' *does* *not* exist for reading."
        self.assertRaises(AssertionError, self._test_readonly, 'PUSH')


class WriteOnlyFunctionListTest(
        FunctionListTestBase, metaclass=GenerateTestCases(
            '_test_writeonly', [(i,) for i in WRONLY_FUNCTION_LIST])):
    "Test that a bunch of functions exist for writing only."

    def _test_writeonly(self, function):
        "Test that Function '{}' exists for writing only (generated test)."
        self.readfunc(function)
        self.assertLinted({'E_FUNC_WRONLY': 1})

        self.writefunc(function)
        self.assertLinted({})

    def test_POP(self):
        "Test that Function 'POP' *does* *not* exist for writing."
        self.assertRaises(AssertionError, self._test_writeonly, 'PUSH')

    @expectedFailure
    def test_PUSH(self):
        "Test that Function 'PUSH' exists for writing only."
        self._test_writeonly('PUSH')
