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
            # We've added exceptions so 0-9A-Za-z sorts before other
            # patterns; because [0-9+#*] is a common pattern.
            ('_[0-26-94]', '_[0-246-9]'),
            ('_[A-Z0-9+]', '_[0-9A-Z+]'),
            ('_[A-EQc-z0-9+#*]', '_[0-9A-EQc-z#*+]'),
            ('_[23]xx', '_[23]XX'),
            ('_[+abs]', '_[abs+]'),
            ('_[{Aa@QqZz`]', '_[AQZaqz@`{]'),
        )
        for a, b in synonyms:
            pattern = Pattern(a, None)
            self.assertEqual(pattern.canonical_pattern, b)
