from asterisklint.alinttest import ALintTestCase
from asterisklint.pattern import Pattern


class CanonicalPatternTest(ALintTestCase):
    def test_canonical(self):
        synonyms = (
            ('_100', '100'),    # pattern-form is not a pattern
            ('1-0-0', '100'),   # dashes are removed (FIXME? do we want that?)
            ('_X[0-9]X!', '_XXX!'),
            ('_N[23456789]', '_NN'),
            ('_[1-9876]', '_Z'),
            ('_xorxor', '_XorXor'),     # FIXME: should be X-or-X-or
            ('_[n][a][m][e][d]-[123]', '_[n]amed[1-3]'),
            ('_[N][n][X][x][Z][z][.][!]', 'NnXxZz.!'),
            ('_X[N][n][X][x][Z][z][.][!]', '_X[N][n][X][x][Z][z][.][!]'),
        )
        for a, b in synonyms:
            pattern = Pattern(a, None)
            self.assertEqual(pattern.canonical_pattern, b)
