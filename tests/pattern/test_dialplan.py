from asterisklint import FileDialplanParser
from asterisklint.alinttest import ALintTestCase


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
