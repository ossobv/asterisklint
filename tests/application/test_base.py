from asterisklint.alinttest import ALintTestCase
from asterisklint.app.base import AppBase
from asterisklint.app.vall.app_voicemail import VoiceMail
from asterisklint.variable import VarLoader
from asterisklint.where import DUMMY_WHERE


class AppBaseSeparateArgsTest(ALintTestCase):
    def test_abc_def_ghi(self):
        self.assertEqual(
            AppBase.separate_args('abc,def,ghi'),
            ['abc', 'def', 'ghi'])

    def test_quoted_abc(self):
        self.assertEqual(
            AppBase.separate_args('"abc"'),
            ['abc'])

    def test_quoted_abc_def(self):
        self.assertEqual(
            AppBase.separate_args('"abc",def'),
            ['abc', 'def'])

    def test_quoted_abc_def_ghi(self):
        self.assertEqual(
            AppBase.separate_args('abc,"def","ghi"'),
            ['abc', 'def', 'ghi'])

    def test_other_delimiter(self):
        self.assertEqual(
            AppBase.separate_args('a,b,c|"d,e,f"|"ghi"', '|'),
            ['a,b,c', 'd,e,f', 'ghi'])

    def test_respect_quotes(self):
        self.assertEqual(
            AppBase.separate_args('"a,b,c","d",e,f'),
            ['a,b,c', 'd', 'e', 'f'])

    def test_respect_quotes_raw(self):
        self.assertEqual(
            AppBase.separate_args(
                '"a,b,c","d",e,f', remove_quotes_backslashes=False),
            ['"a,b,c"', '"d"', 'e', 'f'])

    def test_respect_backslashes(self):
        self.assertEqual(
            AppBase.separate_args('"abc\\",\\"def"'),
            ['abc","def'])

    def test_respect_backslashes_raw(self):
        self.assertEqual(
            AppBase.separate_args(
                '"abc\\",\\"def"', remove_quotes_backslashes=False),
            ['"abc\\",\\"def"'])

    def test_respect_brackets(self):
        self.assertEqual(
            AppBase.separate_args('abc,def[g[h[i],j],kl],mno'),
            ['abc', 'def[g[h[i],j],kl]', 'mno'])

    def test_respect_parens(self):
        self.assertEqual(
            AppBase.separate_args('abc,def(g(h(i),j),kl),mno'),
            ['abc', 'def(g(h(i),j),kl)', 'mno'])

    def test_respect_no_negative_close(self):
        self.assertEqual(
            AppBase.separate_args('abc)))(((,))),def'),
            ['abc)))(((,)))', 'def'])

    def test_respect_brackets_parens(self):
        # TODO: crazy bracket/parens combinations, we should warn here..
        self.assertEqual(
            AppBase.separate_args('abc,def[g(h]i(,j],k)),l],m([),]n)o'),
            ['abc', 'def[g(h]i(,j],k))', 'l]', 'm([),]n)o'])


class AppBaseCallTest(ALintTestCase):
    def call_app(self, appclass, data):
        where = DUMMY_WHERE
        app = appclass()
        var = VarLoader().parse_variables(data, where)
        app(var, where)

    def test_abcdefghi(self):
        self.call_app(AppBase, 'abc,def,ghi')

    def test_variables(self):
        self.call_app(AppBase, '${abc},def,ghi')

    def test_voicemail(self):
        self.call_app(VoiceMail, '${abc},s')
