from functools import total_ordering

# TODO: two classes of errors?
# - in-pattern errors
# - in-dialplan errors (inconsistent used of same-valued pattern, or
#   could we catch this by using a single canonical form only?)


# Pattern info:
#
# X Z N   match ranges 0-9, 1-9, 2-9 respectively.
# [       denotes the start of a set of character. Everything inside
#         is considered literally. We can have ranges a-d and individual
#         characters. A '[' and '-' can be considered literally if they
#         are just before ']'.
#         (currently there is no way to specify ']' in a range, nor \ is
#         considered specially.)
#
# General problems:
#
# - trip on lowercase
# - trip on inconsistent use of pattern styles (combining [0-9] with X)
# - trip on backslashes and spaces in patterns
# - trip on unescaped undelimited XZN between other letters
#   (_snake-! == _s[0-9]ake-!, should be _s[n]ake-!)
# - trip on empty charset
# - ...
# - ...
#
# Pattern order:
#
# Patterns are ordered from left to right, by matchcharacter, where a
# matchcharacter can be one of these.
# - 0x001xx     one character, character set starting with xx
# - 0x0yyxx     yy characters, character set starting with xx
# - 0x18000     '.' (one or more of anything)
# - 0x28000     '!' (zero or more of anything)
# - 0x30000     NUL (end of string) <-- ? needed
# - 0x40000     error in set.
#
# However(!), when sorting, the non-pattern comes before a pattern
# (see ext_cmp()).


@total_ordering  # now we only need 'eq' and 'lt'
class Pattern(object):
    NOT_A_PATTERN = 0
    IS_A_PATTERN = 1

    # Pattern heeft equality tests zodat "s-zap" == "s-[1-9]ap", maar emit
    # wel een warning als je hier iets anders neerzet! (Zelfde verhaal
    # met hoofdletters vs. kleine letters.)
    def __init__(self, pattern, where):
        self.raw = pattern
        self.where = where

        # Values should hold an array of unsigneds:
        # (u32, u32, u32, ...)
        #
        # There the first integer defines the pattern type (value or
        # pattern) and the second value is a single integral value as
        # mentioned in the pattern value-list above.
        #
        # 100     = (0, 0x31, 0x030, 0x30)
        # _20     = (1, 0x32, 0x031)
        # _2[0-2] = (1, 0x32, 0x330)
        #
        # Unless the pattern has gaps, in which case we store it as a
        # tuple instead.
        #
        # _2[013] = (1, (0x32,), (0x330, b'013'))
        #
        # This would require us to marshal patterns to the same type
        # before comparing the values. And that complicates things.
        # Let's live with the space complexity for now and cast all
        # to a list of tuples.
        #
        # Note that according to asizeof [1] a relatively simple pattern
        # like "_s-[0-259]" translates to (1, (371,), (1328, b'01259'))
        # which takes up 328 bytes.
        # [1] http://code.activestate.com/recipes/546530/
        #
        # We could consider investing in making the pattern a Fly-Weight
        # or Singleton, so it doesn't consume more memory than it has
        # to.
        #
        self.values = self.parse(pattern)

    @classmethod
    def parse(cls, raw):
        "Takes str, returns tuple."
        if not raw:
            return tuple(-1, (0x40000,))  # bad pattern

        if raw[0] == '_':
            return tuple([Pattern.IS_A_PATTERN] + cls.parse_pattern(raw[1:]))

        return tuple(
            [Pattern.NOT_A_PATTERN] +
            [(0x100 + i,) for i in bytes(raw, 'utf-8') if i != 0x2d])

    @classmethod
    def parse_pattern(cls, raw):
        "Takes str, returns list."""
        raw = list(bytes(raw, 'utf-8'))
        ret = []
        while raw:
            num = raw.pop(0)
            if num == 0x2d:             # '-'
                pass
            elif num in (0x58, 0x78):   # 'X'/'x'
                ret.append((0xa30,))    # (10 * 0x100) + ord('0')
            elif num in (0x5a, 0x7a):   # 'Z'/'z'
                ret.append((0x931,))    # (9 * 0x100) + ord('1')
            elif num in (0x4e, 0x6e):   # 'N'/'n'
                ret.append((0x832,))    # (8 * 0x100) + ord('2')
            elif num == 0x2e:           # '.'
                ret.append((0x18000,))
            elif num == 0x21:           # '!'
                ret.append((0x28000,))
            elif num == 0x5b:           # '['
                try:
                    range_end = raw.index(0x5d)  # ']'
                except IndexError:
                    # TODO: raise error!
                    ret.append((0x40000,))
                    break
                ret.append(cls.parse_range_list(raw[0:range_end]))
                raw = raw[(range_end + 1):]  # drop ']'
            else:
                # TODO: warn on closing bracket or other non-standard
                # characters
                ret.append((0x100 + num,))

        return ret

    @classmethod
    def parse_range_list(cls, rawlist):
        "Takes list, returns number."""
        # TODO: check empty list?
        # TODO: complain about backslashes?
        # TODO: warn on [-0-9] (prefer [0-9-])
        usedlist = []
        while len(rawlist) >= 3:
            if rawlist[1] == 0x2d:  # rawlist[0] '-' rawlist[2]
                a, b = rawlist[0], rawlist[2]
                if a > b:
                    # TODO: complain
                    a, b = b, a  # swap
                usedlist.extend(range(a, b + 1))
                rawlist = rawlist[3:]
            else:
                a = rawlist.pop(0)
                usedlist.append(a)

        # At this point, there are at most two items left.
        usedlist.extend(rawlist)

        # Is the list unequal to the set: complain.
        usedset = set(usedlist)
        if len(usedset) != len(usedlist):
            # print('TODO/FIXME/COMPLAIN:', usedset, usedlist)
            pass

        # Numeric value.
        usedlist = list(usedset)
        usedlist.sort()
        num = len(usedlist) * 0x100 | usedlist[0]

        # Check if usedlist has gaps, if it has, then return a tuple
        # instead of a single value.
        if len(usedlist) > 1 and (
                usedlist[-1] - usedlist[0] != len(usedlist) - 1):
            return (num, bytes(usedlist))

        return (num,)

    def matches_same(self, other):
        """
        Same as regular equal, but this time, ignore whether this is
        a pattern or not.
        """
        if other is None:
            return False
        return self.values[1:] == other.values[1:]

    def __hash__(self):
        return hash(self.values)

    def __eq__(self, other):
        if other is None:
            return False
        return self.values == other.values

    def __lt__(self, other):
        if other is None:
            return False
        return self.values < other.values

    def __repr__(self):
        return '<Pattern({})>'.format(self.raw or '')

    def __str__(self):
        return self.raw
