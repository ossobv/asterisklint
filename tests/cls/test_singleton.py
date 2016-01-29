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
from asterisklint.cls import Singleton
from asterisklint.alinttest import ALintTestCase


class TestSingleton(metaclass=Singleton):
    def __init__(self, foo=None):
        self.foo = foo or 'bar'


class TestSingletonWithReinit(metaclass=Singleton):
    def __init__(self, foo=None):
        self.foo = foo or 'bar'

    def reinit(self, foo=None):
        if foo and self.foo != foo:
            raise ValueError(
                'Reinitializing {} with arg {!r} conflicts with '
                'previous arg {!r}'.format(
                    self.__class__.__name__, foo, self.foo))


class SingletonTest(ALintTestCase):
    def test_singleton(self):
        s = TestSingleton()                     # no args, gets 'bar'
        self.assertEqual(s.foo, 'bar')

        s2 = TestSingleton('def')               # different args
        self.assertEqual(s2.foo, 'bar')         # unchanged
        self.assertEqual(s, s2)

        s3 = TestSingleton('bar')               # same args
        self.assertEqual(s, s3)                 # also unchanged, obviously

    def test_singleton_with_reinit(self):
        s = TestSingletonWithReinit('abc')      # 'abc' args
        self.assertEqual(s.foo, 'abc')

        s2 = TestSingletonWithReinit('abc')     # same args
        self.assertEqual(s2.foo, 'abc')         # unchanged
        self.assertEqual(s, s2)

        s3 = TestSingletonWithReinit()          # no args
        self.assertEqual(s3.foo, 'abc')         # unchanged
        self.assertEqual(s, s3)

        # Trying to change the args this time, will fail.
        self.assertRaises(ValueError, TestSingletonWithReinit, 'bar')
