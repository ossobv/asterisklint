from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase
from asterisklint.pattern import Pattern


class PatternOrderTest(ALintTestCase):
    def test_equals(self):
        synonyms = (
            ('100', '_100'),    # pattern-form
            ('100', '1-0-0'),   # dashes are invisible
            ('100', '_1-0-0'),  # pattern and dashes
            ('_X', '_[0-9]'),   # X == 0..9
            ('_Z', '_[1-9]'),   # X == 0..9
            ('_N', '_[2-9]'),   # X == 0..9
            ('_X', '_x'),       # lowercase
            ('_Z', '_z'),       # lowercase
            ('_N', '_n'),       # lowercase
            ('-_', '_-_'),      # .. nasty
            ('----12', '12'),   # .. nasty
            ('12----', '12'),   # .. nasty
        )
        for a, b in synonyms:
            pata = Pattern(a, None)
            patb = Pattern(b, None)
            if not pata.matches_same(patb):
                raise AssertionError(
                    "{} should match same as {} but doesn't".format(
                        pata, patb))
            if not patb.matches_same(pata):
                raise AssertionError(
                    "{} should match same as {} but doesn't".format(
                        patb, pata))


class PatternDialplanTest(ALintTestCase):
    def do_patterns(self, snippet):
        data = '''\
[general]

[globals]

[non_empty_context]
{}'''.format(snippet).encode('ascii')

        reader = self.create_instance_and_load_single_file(
            FileDialplanParser, 'test.conf', data)

        out = [i for i in reader]
        self.assertEqual(len(out), 1)
        dialplan = out[0]
        self.assertEqual(len(dialplan.contexts), 1)
        context = dialplan.contexts[0]
        return [i.pattern for i in context]

    def test_normal(self):
        patterns = self.do_patterns('''\
exten => s,1,NoOp(s,1)
exten => s,n,NoOp(s,2)
exten => 100,1,NoOp(100,1)
exten => 100,n,NoOp(100,2)
exten => 100,n,NoOp(100,3)
exten => 101,1,NoOp(101,1)
exten => _X!,1,NoOp(_X!,1)
exten => _X!,n,NoOp(_X!,2)
''')
        self.assertEqual(
            [i.raw for i in patterns],
            ['s', 's', '100', '100', '100', '101', '_X!', '_X!'])
