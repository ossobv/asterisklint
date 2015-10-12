from asterisklint.alinttest import ALintTestCase
from asterisklint.application import Variable, VarsLoader
from asterisklint.where import DUMMY_WHERE


class NormalTest(ALintTestCase):
    def test_var_abc(self):
        var = VarsLoader().substitute_variables(
            '${abc}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable('abc'))
        self.assertEqual(
            str(var), '${abc}')
        self.assertEqual(
            var.format(abc='ABC'), 'ABC')

    def test_var_abc_def(self):
        var = VarsLoader().substitute_variables(
            '${abc}${def}', DUMMY_WHERE)
        self.assertEqual(
            var, Variable.join([Variable('abc'), Variable('def')]))
        self.assertEqual(
            str(var), '${abc}${def}')
        self.assertEqual(
            var.format(abc='ABC', **{'def': 'DEF'}), 'ABCDEF')

    def test_var_abc_def_with_otherdata(self):
        var = VarsLoader().substitute_variables(
            '//${abc}[$]${def}$$', DUMMY_WHERE)
        self.assertEqual(
            var, Variable.join([
                '//', Variable('abc'), '[$]', Variable('def'), '$$']))
        self.assertEqual(
            str(var), '//${abc}[$]${def}$$')
        self.assertEqual(
            var.format(abc='ABC', **{'def': 'DEF'}), '//ABC[$]DEF$$')
