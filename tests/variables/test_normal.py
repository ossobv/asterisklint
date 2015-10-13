from asterisklint.alinttest import ALintTestCase
from asterisklint.application import Variable, VarsLoader
from asterisklint.where import DUMMY_WHERE


class NormalTest(ALintTestCase):
    def test_var_foo(self):
        var = VarsLoader().substitute_variables(
            '${foo}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable('foo'))
        self.assertEqual(
            str(var), '${foo}')
        self.assertEqual(
            var.format(foo='ABC'), 'ABC')

    def test_var_foo_bar(self):
        var = VarsLoader().substitute_variables(
            '${foo}${bar}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable.join([Variable('foo'), Variable('bar')]))
        self.assertEqual(
            str(var), '${foo}${bar}')
        self.assertEqual(
            var.format(foo='ABC', **{'bar': 'DEF'}), 'ABCDEF')

    def test_var_foo_bar_with_otherdata(self):
        var = VarsLoader().substitute_variables(
            '//${foo}[$]${bar}$$', DUMMY_WHERE)
        self.assertEqual(
            var, Variable.join([
                '//', Variable('foo'), '[$]', Variable('bar'), '$$']))
        self.assertEqual(
            str(var), '//${foo}[$]${bar}$$')
        self.assertEqual(
            var.format(foo='ABC', bar='DEF'), '//ABC[$]DEF$$')

    def test_simple_var_in_var(self):
        var = VarsLoader().substitute_variables(
            '${${foo}}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable(Variable('foo')))
        self.assertEqual(
            str(var), '${${foo}}')
        self.assertEqual(
            var.format(foo='bar', bar='DEF'), 'DEF')

    def test_joined_var_in_var(self):
        var = VarsLoader().substitute_variables(
            '${${a}a${c}}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable(Variable.join([
                Variable('a'), 'a', Variable('c')])))
        self.assertEqual(
            str(var), '${${a}a${c}}')
        self.assertEqual(
            var.format(a='b', c='r', bar='DEF'), 'DEF')
