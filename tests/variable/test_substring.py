from asterisklint.alinttest import ALintTestCase
from asterisklint.variable import Var, VarLoader
from asterisklint.where import DUMMY_WHERE


class SubstringTest(ALintTestCase):
    def test_var_begin(self):
        var = VarLoader().parse_variables('${foo:0:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=0, length=2))
        self.assertEqual(
            str(var), '${foo:0:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'AB')

    def test_var_offset(self):
        var = VarLoader().parse_variables('${foo:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=2))
        self.assertEqual(
            str(var), '${foo:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'CDEF')

    def test_var_middle(self):
        var = VarLoader().parse_variables('${foo:2:3}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=2, length=3))
        self.assertEqual(
            str(var), '${foo:2:3}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'CDE')

    def test_var_end(self):
        var = VarLoader().parse_variables('${foo:-2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=-2))
        self.assertEqual(
            str(var), '${foo:-2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'EF')
