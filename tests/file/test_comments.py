from asterisklint.alinttest import ALintTestCase
from asterisklint.file import FileReader


class CommentsTest(ALintTestCase):
    maxDiff = 1024

    def test_normal(self):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf', b'''\
;; vim: set fenc=utf-8 et:
;; A short explanation about this,
;; and that.

[general] ; the general context must exist, blah blah
; The magic flag must be enabled for the frobnication to work.
magic=yes   ; once upon a time, there was a long
            ; help text that spanned multiple lines.
            ; in fact, it was so long, that a comment
            ; stripping parser would complain about the
            ; voidness.
frobnication=always

;; The rest of this file will hold other stuff.

[stuff]

[more-stuff]
with_actual_values=1 ; these may certainly be duplicate
with_actual_values=2
with_actual_values=3
this_is_not_a_comment=semi\\;delimited; but this is a comment
''')
        out = [i for i in reader]
        self.assertEqual(
            [i[1] for i in out],
            ['',
             '',
             '',
             '',
             '[general]',
             '',
             'magic=yes',
             '',
             '',
             '',
             '',
             'frobnication=always',
             '',
             '',
             '',
             '[stuff]',
             '',
             '[more-stuff]',
             'with_actual_values=1',
             'with_actual_values=2',
             'with_actual_values=3',
             'this_is_not_a_comment=semi;delimited'])
        self.assertEqual(
            [i[2] for i in out],
            [';; vim: set fenc=utf-8 et:',
             ';; A short explanation about this,',
             ';; and that.',
             '',
             ' ; the general context must exist, blah blah',
             '; The magic flag must be enabled for the frobnication to work.',
             '   ; once upon a time, there was a long',
             '            ; help text that spanned multiple lines.',
             '            ; in fact, it was so long, that a comment',
             '            ; stripping parser would complain about the',
             '            ; voidness.',
             '',
             '',
             ';; The rest of this file will hold other stuff.',
             '',
             '',
             '',
             '',
             ' ; these may certainly be duplicate',
             '',
             '',
             '; but this is a comment'])

        # "this_is_not_a_comment=semi\\;delimited; but this is a comment"
        # - W_WSH_COMMENT -----------------------^ (missing leading space)
        self.assertLinted({'W_WSH_COMMENT': 1})

    def test_escaped_space(self):
        # Asterisk won't do any magic with the backslash, not even for
        # the backslash itself. It will only react to escaped semi's.
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf', b'''\
[general]
value1=\\\x20
value2=\\  ; with comment
value3=\\; ; with comment
value4=\\\\;\\;; with comment
''')
        out = [i for i in reader]
        self.assertEqual([i[1] for i in out],
                         ['[general]',
                          'value1=\\',
                          'value2=\\',
                          'value3=;',
                          'value4=\\;;'])
        self.assertEqual([i[2] for i in out],
                         ['', '', '  ; with comment', ' ; with comment',
                          '; with comment'])
        # value1 with trailing \x20 will trigger a W_WSH_EOL warning.
        # vaule4 with missing \x20 will trigger a W_WSH_COMMENT warning.
        self.assertLinted({'W_WSH_EOL': 1, 'W_WSH_COMMENT': 1})


class CommentWithoutWhitespaceTest(ALintTestCase):
    def string_test(self, string):
        reader = self.create_instance_and_load_single_file(
            FileReader, 'test.conf', '{}\n'.format(string).encode('utf-8'))
        out = [i for i in reader]
        del out

    def test_no_problem(self):
        self.string_test(';\\;')    # don't care about contents of comment
        self.string_test('x\\;x')   # there is no comment
        self.string_test('x\\;x ;no problem')  # the comment space is ok

    def test_missing_space(self):
        # We don't want a semi inside the value. Complain about the lack
        # of space before it.
        self.string_test('x=y;')
        self.assertLinted({'W_WSH_COMMENT': 1})

    def test_missing_space_after_escaped_semi(self):
        # We don't want a semi inside the value. Complain about the lack
        # of space before it.
        self.string_test('x=y\;z;')
        self.assertLinted({'W_WSH_COMMENT': 1})
