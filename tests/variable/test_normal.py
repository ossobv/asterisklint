from asterisklint.alinttest import ALintTestCase
from asterisklint.varfun import VarLoader
from asterisklint.variable import Var
from asterisklint.where import DUMMY_WHERE


class NormalTest(ALintTestCase):
    def test_var_foo(self):
        var = VarLoader().parse_variables('${foo}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo'))
        self.assertEqual(
            str(var), '${foo}')
        self.assertEqual(
            var.format(foo='ABC'), 'ABC')

    def test_var_foo_bar(self):
        var = VarLoader().parse_variables('${foo}${bar}', DUMMY_WHERE)
        self.assertEqual(
            var, Var.join([Var('foo'), Var('bar')]))
        self.assertEqual(
            str(var), '${foo}${bar}')
        self.assertEqual(
            var.format(foo='ABC', **{'bar': 'DEF'}), 'ABCDEF')

    def test_var_foo_bar_with_otherdata(self):
        var = VarLoader().parse_variables('//${foo}[$]${bar}$$', DUMMY_WHERE)
        self.assertEqual(
            var, Var.join(['//', Var('foo'), '[$]', Var('bar'), '$$']))
        self.assertEqual(
            str(var), '//${foo}[$]${bar}$$')
        self.assertEqual(
            var.format(foo='ABC', bar='DEF'), '//ABC[$]DEF$$')

    def test_simple_var_in_var(self):
        var = VarLoader().parse_variables('${${foo}}', DUMMY_WHERE)
        self.assertEqual(
            var, Var(Var('foo')))
        self.assertEqual(
            str(var), '${${foo}}')
        self.assertEqual(
            var.format(foo='bar', bar='DEF'), 'DEF')

    def test_joined_var_in_var(self):
        var = VarLoader().parse_variables('${${a}a${c}}', DUMMY_WHERE)
        self.assertEqual(
            var, Var(Var.join([Var('a'), 'a', Var('c')])))
        self.assertEqual(
            str(var), '${${a}a${c}}')
        self.assertEqual(
            var.format(a='b', c='r', bar='DEF'), 'DEF')
