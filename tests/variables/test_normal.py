from asterisklint.alinttest import ALintTestCase
from asterisklint.application import VarsLoader
from asterisklint.where import DUMMY_WHERE


class NormalTest(ALintTestCase):
    def test_var_abc(self):
        self.assertEqual(
            VarsLoader().substitute_variables(
                '${abc}', DUMMY_WHERE),
            'variable_abc')

    def test_var_abc_def(self):
        self.assertEqual(
            VarsLoader().substitute_variables(
                '${abc}${def}', DUMMY_WHERE),
            'variable_abcvariable_def')

    def test_var_abc_def_with_otherdata(self):
        self.assertEqual(
            VarsLoader().substitute_variables(
                '//${abc}[$]${def}$$', DUMMY_WHERE),
            '//variable_abc[$]variable_def$$')
