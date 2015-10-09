from asterisklint.alinttest import ALintTestCase
from asterisklint.pattern import Pattern


class CanonicalPatternTest(ALintTestCase):
    def test_canonical(self):
        """Compare the raw pattern with the canonical pattern."""
        synonyms = (
            ('_100', '100'),    # pattern-form is not a pattern
            ('1-0-0', '100'),   # dashes are removed (FIXME? do we want that?)
            ('_X[0-9]X!', '_XXX!'),
            ('_N[23456789]', '_NN'),
            ('_[1-9876]', '_Z'),
            ('_xorxor', '_XorXor'),     # FIXME: should be X-or-X-or?
            ('_[n][a][m][e][d]-[1-4]', '_[n]amed[1-4]'),
            ('_[N][n][X][x][Z][z][.][!]', 'NnXxZz.!'),
            ('_X[N][n][X][x][Z][z][.][!]', '_X[N][n][X][x][Z][z][.][!]'),
            # We've added exceptions so 0-9A-Za-z sorts before other
            # patterns; because [0-9+#*] is a common pattern.
            ('_[0-26-94]', '_[01246-9]'),
            ('_[A-Z0-9+]', '_[0-9A-Z+]'),
            ('_[A-EQc-z0-9+#*]', '_[0-9A-EQc-z#*+]'),
            ('_[23]xx', '_[23]XX'),
            ('_[+abs]', '_[abs+]'),
            ('_[{Aa@QqZz`]', '_[AQZaqz@`{]'),
        )
        for a, b in synonyms:
            pattern = Pattern(a, None)
            self.assertEqual(pattern.canonical_pattern, b)

    def test_is_canonical(self):
        """Test the is_canonical property, which may return True even
        though raw != canonical, because the user may have placed dashes
        for clarity."""
        already_good = (
            '100',
            '1-0-0',
            # Short patterns are not made into ranges.
            '_[01]',
            '_[012]',
            '_[013]',
            '_[0134]',
            # Longer ranges are.
            '_[0-3]',
            '_[0-4]',
            # Other tests.
            '_XXX!',
            '_ZN[3-9]',
            '_XorXor',  # FIXME: should be X-or-X-or?
            '1-0-0-',   # FIXME: we don't want trailing dashes
            '-1-0-0',   # FIXME: we don't want leading dashes
            '_[n]amed[1-5]',
            's-yes',
            't',
            '_1NN-XXX!',
            '_[01246-9]',
            '_[1-46-9]',
            '_[1236-9]',
            '_[0-9A-Z+]',
            '_[0-9A-EQc-z#*+]',
        )
        for a in already_good:
            pattern = Pattern(a, None)
            if not pattern.is_canonical:
                raise AssertionError(
                    'pattern {!r} does not pass as canonical form, '
                    'expected {!r}'.format(
                        pattern.raw, pattern.canonical_pattern))

    def test_is_not_canonical(self):
        """Test the negative side of the is_canonical property."""
        not_good = (
            '_100',
            '_X[0-9]X!',
            '_ZN[2-9]',
            '_xorxor',
            '_named[1-3]',
            '_[1-46-94]',
            '_[0126-94]',
            '_[A-Z0-9+]',
        )
        for a in not_good:
            pattern = Pattern(a, None)
            if pattern.is_canonical:
                raise AssertionError(
                    'pattern {!r} is wrongly passed as canonical form'.format(
                        pattern.raw))
