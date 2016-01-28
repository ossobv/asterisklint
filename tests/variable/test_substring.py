from asterisklint.alinttest import ALintTestCase
from asterisklint.varfun import VarLoader
from asterisklint.variable import Var
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

    def test_var_endmiddle(self):
        var = VarLoader().parse_variables('${foo:-3:2}', DUMMY_WHERE)
        self.assertEqual(
            var, Var('foo', start=-3, length=2))
        self.assertEqual(
            str(var), '${foo:-3:2}')
        self.assertEqual(
            var.format(foo='ABCDEF'), 'DE')

    def test_invalid_args(self):
        VarLoader().parse_variables('${foo:1:2:3}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_ARGS': 1})

    def test_invalid_start(self):
        # blank
        VarLoader().parse_variables('${foo:}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # garbage
        VarLoader().parse_variables('${foo:x}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # 0-offset
        VarLoader().parse_variables('${foo:0}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

        # blank with length
        VarLoader().parse_variables('${foo::2}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_START': 1})

    def test_invalid_length(self):
        # blank
        VarLoader().parse_variables('${foo:0:}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # garbage
        VarLoader().parse_variables('${foo:0:x}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # 0-length
        VarLoader().parse_variables('${foo:2:0}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # negative length
        VarLoader().parse_variables('${foo:0:-2}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

        # length as large as negative offset
        VarLoader().parse_variables('${foo:-2:1}', DUMMY_WHERE)  # ok
        VarLoader().parse_variables('${foo:-2:2}', DUMMY_WHERE)
        self.assertLinted({'E_VAR_SUBSTR_LENGTH': 1})

    def test_slice_by_variable_start(self):
        var = VarLoader().parse_variables('${foo:${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:${tmp}}')

    def test_slice_by_variable_negstart(self):
        var = VarLoader().parse_variables('${foo:-${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:-${tmp}}')

    def test_slice_by_variable_length(self):
        var = VarLoader().parse_variables('${foo:1:${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:1:${tmp}}')

    def test_slice_by_variable_neglength(self):
        var = VarLoader().parse_variables('${foo:1:-${tmp}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:1:-${tmp}}')

    def test_slice_by_two_variables(self):
        var = VarLoader().parse_variables('${foo:${x}:-${y}}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:${x}:-${y}}')

    def test_slice_by_expression(self):
        var = VarLoader().parse_variables('${foo:$[1+1]:$[2+2]}', DUMMY_WHERE)
        self.assertEqual(str(var), '${foo:$[1+1]:$[2+2]}')
