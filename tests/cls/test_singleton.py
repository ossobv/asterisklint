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
