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
# - 0x30000     NUL (end of string)
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
        self.values = self.parse(pattern)

    @classmethod
    def parse(cls, raw):
        if not raw:
            return (-1, 0x40000)  # bad pattern

        if raw[0] == '_':
            return tuple((Pattern.IS_A_PATTERN,) + cls.parse_pattern(raw[1:]))

        return tuple(
            [Pattern.NOT_A_PATTERN] +
            [(0x100 + i) for i in bytes(raw, 'utf-8') if i != 0x2d])

    @classmethod
    def parse_pattern(cls, raw):
        raw = list(bytes(raw, 'utf-8'))
        ret = []
        while raw:
            num = raw.pop(0)
            if num == 0x2d:             # '-'
                pass
            elif num in (0x58, 0x78):   # 'X'/'x'
                ret.append(0xa30)       # (10 * 0x100) + ord('0')
            elif num in (0x5a, 0x7a):   # 'Z'/'z'
                ret.append(0x931)       # (9 * 0x100) + ord('1')
            elif num in (0x4e, 0x6e):   # 'N'/'n'
                ret.append(0x832)       # (8 * 0x100) + ord('2')
            elif num == 0x2e:           # '.'
                ret.append(0x18000)
            elif num == 0x21:           # '!'
                ret.append(0x28000)
            elif num == 0x5b:           # '['
                try:
                    range_end = raw.index(0x5d)  # ']'
                except IndexError:
                    # TODO: raise error!
                    ret.append(0x40000)
                    break
                ret.append(cls.parse_range_list(raw[0:range_end]))
                raw = raw[(range_end + 1):]  # drop ']'
            else:
                # TODO: warn on closing bracket or other non-standard
                # characters
                ret.append(0x100 + num)

        return tuple(ret)

    @classmethod
    def parse_range_list(cls, raw):
        # Slightly different interface: takes a list() and returns a
        # number. The others take a str() and return a tuple().
        # TODO: complain about backslashes?
        # TODO: warn on [-0-9] (prefer [0-9-])
        usedlist = []
        while len(raw) >= 3:
            if raw[1] == 0x2d:  # raw[0] '-' raw[2]
                a, b = raw[0], raw[2]
                if a > b:
                    # TODO: complain
                    a, b = b, a  # swap
                usedlist.extend(range(a, b + 1))
                raw = raw[3:]
            else:
                usedlist.extend(raw[0])
                raw.pop(0)

        # At this point, there are at most two items left.
        while raw:
            usedlist.extend(raw[0])
            raw.pop(0)

        # Is the list unequal to the set: complain.
        usedset = set(usedlist)
        if len(usedset) != len(usedlist):
            # print('TODO/FIXME/COMPLAIN:', usedset, usedlist)
            pass

        # TODO: fixme, we need the usedset converted to some binary
        # representation so we can compare sets like:
        # [049] < [059] because they both score the same (len=3, low=0)
        # but the former is lower.

        # Order it again, take the lowest value and count.
        usedlist = list(usedset)
        usedlist.sort()
        return len(usedlist) * 0x100 | usedlist[0]

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
