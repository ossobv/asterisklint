from asterisklint.alinttest import ALintTestCase
from asterisklint.pattern import Pattern


class PatternOrderTest(ALintTestCase):
    def test_equals(self):
        synonyms = (
            ('100', '_100'),    # pattern-form
            ('100', '1-0-0'),   # dashes are invisible
            ('100', '_1-0-0'),  # pattern and dashes
            ('_X', '_[0-9]'),   # X == 0..9
            ('_Z', '_[1-9]'),   # Z == 1..9
            ('_N', '_[2-9]'),   # N == 2..9
            ('_N', '_[23-56-89]'),
            ('_N', '_[23456789]'),
            ('_N', '_[2-92-92-9]'),
            ('_X', '_x'),       # lowercase
            ('_Z', '_z'),       # lowercase
            ('_N', '_n'),       # lowercase
            ('-_', '_-_'),      # .. nasty
            ('----12', '12'),   # .. nasty
            ('12----', '12'),   # .. nasty
        )
        for a, b in synonyms:
            self.assertMatchesSame(Pattern(a, None), Pattern(b, None))

    def test_lower(self):
        is_lower = (
            # Simple tests.
            ('100', '101'),     # regular values
            ('1-0-0', '101'),   # dashes are still invisible
            ('100', '1-0-1'),   # dashes are still invisible
            ('A', 'B'),         # letters are fine
            ('A', 'a'),         # case sensitive
            ('0', 'A'),         # ascii table rules
            # Longer or shorter?
            ('000', '0000'),    # shortest match wins for non-patterns
            ('_XXX', '_XX'),    # longest match wins for patterns
            # Non-patterns are always ordered lower than patterns.
            ('100', '_100'),
            ('2222', '_100'),
            # Patterns are ordered by size and then by starting letter.
            ('_N', '_Z'),
            ('_N', '_[1-9]'),   # equals to _Z
            ('_Z', '_X'),
            ('_N1', '_N2'),
            ('_N2', '_X1'),
            ('_0N2', '_0X1'),
            # Make it more complicated.
            ('_N2', '_'),
            ('_N2', '_X1'),
            ('_0N2', '_0X1'),
            ('_s-[0-5]', '_s-[1-6]'),   # second one is later
            ('_s-[1-6]', '_s-[0-59]'),  # second one is longer
            # And yet more complicated, with ranges where the middle differs.
            ('_s-[1259]', '_s-[1269]'),     # both with length 4 and start 1
            ('_s-[0-259]', '_s-[01269]'),   # both with length 5 and start 0
            # The other operators.
            ('_.', '_!'),       # period is one-or-more, excl. is zero-or-more
            ('_A.', '_A!'),
            ('_AA', '_A.'),
            ('_AA.', '_AA'),
            ('_AA!', '_AA'),
            ('_AX!', '_B'),     # the order of the earlier bytes count
            ('_AX!', '_B'),     # the order of the earlier bytes count
        )
        for a, b in is_lower:
            self.assertLower(Pattern(a, None), Pattern(b, None))

    def assertMatchesSame(self, pattern_a, pattern_b):
        match_ab = pattern_a.matches_same(pattern_b)
        match_ba = pattern_b.matches_same(pattern_a)
        if match_ab != match_ba:
            raise AssertionError(
                "{} fails its symmetric matchsame relation with {}".format(
                    pattern_a, pattern_b))
        if not match_ab:
            raise AssertionError(
                "{} should match same as {} but doesn't".format(
                    pattern_a, pattern_b))

    def assertLower(self, pattern_a, pattern_b):
        lower_ab = (pattern_a < pattern_b)
        higher_ba = (pattern_b > pattern_a)
        if lower_ab != higher_ba:
            raise AssertionError(
                "{} fails its symmetric lower relation with {}".format(
                    pattern_a, pattern_b))
        if not lower_ab:
            raise AssertionError(
                "{} should be lower than {} but isn't".format(
                    pattern_a, pattern_b))
