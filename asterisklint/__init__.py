#!/usr/bin/env python3
import re
import sys


class LintNotice(object):
    letter = 'N'

    def __init__(self, where):
        print('{} {}: {} ({!r})'.format(
            where, self.__class__.__name__, self.message, where.line))


class LintWarning(LintNotice):
    letter = 'W'


class LintError(LintNotice):
    # TODO: optional: stop at first error
    letter = 'E'


class E_CONF_NOCTX_NOVAR(LintError):
    message = 'expected context or var/object set'
class E_CONF_MISSING_CTX(LintError):
    message = 'expected context before var/object set'
class E_DP_NOT_DPVARSET(LintError):
    message = 'expected exten/same/include, got something else'
class E_ENC_NOT_UTF8(LintError):
    message = 'expected UTF-8 encoding, got something else'
class W_FF_DOS_EOFCRLF(LintWarning):
    message = 'unexpected trailing CRLF in DOS file format'
class W_FF_DOS_BARELF(LintWarning):
    message = 'unexpected bare LF in DOS file format'
class W_FF_UNIX_CRLF(LintWarning):
    message = 'unexpected CRLF in UNIX file format'
class W_FF_UNIX_NOLF(LintWarning):
    message = 'unexpected line without LF in UNIX file format'


# TODO: asterisk config lint
# TODO: asterisk dialplan lint
# TODO: delegate globals lintage to Config lint
# TODO: create the possibility for Asterisk version differences
# TODO: allow warnings to be suppressed? (always-emit, emit-once, silence)
# TODO: wat voor soort warnings: error (skip/ignore/fail), warning (case
#       fouten of schijnbaar/mogelijke inconsequentie)


class Dialplan(object):
    def __init__(self):
        self.globals = []
        self.contexts = []

    def add_globals(self, globals):
        if self.globals:
            # ERROR: er kan maar 1x globals gedefined worden!
            return
        self.globals = globals

    def format_as_dialplan_show(self):
        # If we have this, we can compare to the asterisk output :)
        pass


class Where(object):
    def __init__(self, filename, lineno, line):
        self.filename = filename  # shared constant in CPython, so cheap
        self.lineno = lineno
        self.line = line
        self.last_line = False

    def __str__(self):
        return '%s:%d' % (self.filename, self.lineno)


class Globals(object):
    pass


class EmptyLine(object):
    def __init__(self, where):
        self.where = where


class Context(object):
    @classmethod
    def from_context(cls, context):
        """
        Use this on subclasses of Context.
        """
        assert not context.varsets
        return cls(context.name, context.templates, context.where)

    def __init__(self, name, templates, where):
        self.name = name
        self.templates = templates
        self.where = where
        self.varsets = []

        if templates:
            E_NOTIMPL_TEMPLATES(where)

    def add(self, varset):
        self.varsets.append(varset)

    def __repr__(self):
        return '[{}]({}) => ({} elements)'.format(
            self.name, self.templates, len(self.varsets))


class DialplanContext(Context):
    def add(self, extension):
        # - If extension.pattern is None ("same") then take previous.
        #   Error if there is none.
        # - If prio is N then assert there is a previous prio with same
        #   pattern.
        self.varsets.append(extension)


class Varset(object):
    def __init__(self, variable, value, arrow, where):
        self.variable = variable
        self.value = value
        self.arrow = arrow  # bool
        self.where = where


class DialplanVarset(object):
    @classmethod
    def from_varset(cls, varset):
        """
        Use this on subclasses of Varset.
        """
        if varset.variable in ('exten', 'same'):
            assert varset.arrow  # W_ARROW
            if varset.variable == 'exten':
                pattern, rest = varset.value.split(',', 1)
            else:
                pattern, rest = None, varset.value

            prio, app = rest.split(',', 1)
            try:
                prio, label = prio.split('(', 1)
            except ValueError:
                prio, label = prio, None
            if prio == 'n':
                prio = None
            elif prio.isdigit():
                prio = int(prio)
            else:
                E_DP_BAD_PRIO(varset.where)
                return None

            if label is not None:
                if not label.endswith(')'):
                    E_DB_BAD_LABEL(varset.where)
                    return None
                label = label[0:-1]
                # TODO: check label validity
            else:
                label = None

            return Extension(pattern, prio, label, app, varset.where)

        elif varset.variable == 'include':
            assert varset.arrow  # W_ARROW
            return Include(varset.value, varset.where)

        else:
            E_DP_NOT_DPVARSET(varset.where)
            return None


class Pattern(object):
    # Pattern heeft equality tests zodat "s-zap" == "s-[1-9]ap", maar emit
    # wel een warning als je hier iets anders neerzet! (Zelfde verhaal
    # met hoofdletters vs. kleine letters.)
    def __init__(self, pattern, where):
        pass


class App(object):
    # App heeft weer z'n eigen parsers en subparsers. Hiermee moeten we ook
    # op kunnen zoeken welke modules er nodig zijn (w00t). Deze komt ook als
    # eerste in aanmerking voor 1.4 vs. 1.8 differences (ExecIf..., vs
    # ExecIf...?)
    # Ook dumpen van alle variabelen (in dat geval moet de subparser aangeven
    # dat een Var geset wordt (Set() en MSet() doen dat bijv.) en ARRAY() en
    # HASH().
    # Parser en subparsers implementeren volgens included modules?
    # Klinkt wat overkill? Maar maakt het wel mooi extensible. De ExecIf()
    # kan dan de args weer splitten en teruggeven...
    #
    # Per subparser kunnen we de versienummers opgeven:
    # SPRINTF() voor < 1.2 => None
    # SPRINTF() voor >= 1.2 < 1.4 => behaviour X
    # SPRINTF() voor >= 1.4 => behaviour Y
    #
    # Hoe pakken we dan app_compat settings voor Set? Hm.
    pass


class Extension(Varset):
    def __init__(self, pattern, prio, label, app, where):
        # Check pattern voor mixen van letters en pattern-letters:
        # - "s-zap" == "s-[1-9]ap" en zou als "s-[z]ap" geschreven moeten
        # - "s-abc" == "sabc"
        # Als pattern is None, dan pakt Context gewoon de vorige, da's
        # prima.
        pass


class BinFileReader(object):
    """
    Reads a file.

    TODO: allow one to specify legal line endings (unix vs dos)
    """
    def __init__(self, filename=None):
        self.filename = filename

    def __iter__(self):
        prev_where, prev_data = None, None

        with open(self.filename, 'rb') as fp:
            for i, line in enumerate(fp):
                if prev_where:
                    yield prev_where, prev_data

                prev_where = Where(self.filename, i + 1, line)
                prev_data = line

        if prev_where:
            prev_where.last_line = True
            yield prev_where, prev_data


class EncodingReader(object):
    def __iter__(self):
        for where, data in super(EncodingReader, self).__iter__():
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                E_ENC_NOT_UTF8(where)
                data = data.decode('cp1252')  # or latin1? or 9?
            yield where, data


class FileformatReader(object):
    """
    TODO: allow one to specify legal line endings (unix vs dos)
    """
    def __iter__(self):
        is_dos = None

        for where, data in super(FileformatReader, self).__iter__():
            has_crlf = data.endswith('\r\n')
            has_lf = data.endswith('\n')

            if is_dos is None:
                is_dos = (has_crlf or not has_lf)

            if is_dos:
                if where.last_line and has_crlf:
                    W_FF_DOS_EOFCRLF(where)
                elif has_lf and not has_crlf:
                    W_FF_DOS_BARELF(where)
            else:
                if where.last_line and not has_lf:
                    W_FF_UNIX_NOLF(where)
                elif has_crlf:
                    W_FF_UNIX_CRLF(where)

            if has_crlf:
                data = data[0:-2]
            elif has_lf:
                data = data[0:-1]

            yield where, data


class AstCommentReader(object):
    # Todo.. strip all comments
    # Todo.. decode the non-comments (backslash remove)
    # Todo.. multiline?
    # Remove whitespace..
    # Todo.. complain about missing whitespace between objects.
    pass


class FileReader(FileformatReader, EncodingReader, BinFileReader):
    pass


class ConfigParser(object):
    # Parse config and emit 1=>X
    # Define who prefers "=>" and who prefers "=". Allow warnings about
    # that to be disabled.
    # Allow templating? Feature v1.1.

    # TODO: compain about too much and/or too little white space!

    regexes = (
        # [context](template1,template2)
        (re.compile(r'^\[([^]]*)\]\s*\(([^)\+])\)$'),
         (lambda where, match: Context(
             name=match.groups()[0], templates=match.groups()[1],
             where=where))),
        # [context]
        (re.compile(r'^\[([^]]*)\]$'),
         (lambda where, match: Context(
             name=match.groups()[0], templates='',
             where=where))),
        # object => value
        (re.compile(r'([^=]*?)\s*=>\s*(.*)$'),
         (lambda where, match: Varset(
             variable=match.groups()[0], value=match.groups()[1],
             arrow=True, where=where))),
        # variable = value
        (re.compile(r'([^=]*?)\s*=\s*(.*)$'),
         (lambda where, match: Varset(
             variable=match.groups()[0], value=match.groups()[1],
             arrow=False, where=where))),
        # (void)
        (re.compile(r'^\s*$'),
         (lambda where, match: EmptyLine(where=where))),
    )

    def __iter__(self):
        for where, data in super(ConfigParser, self).__iter__():
            data = data.strip()
            for regex, func in self.regexes:
                match = regex.match(data)
                if match:
                    value = func(where, match)
                    yield value
                    break
            else:
                E_CONF_BAD_LINE(where)


class EmptyLinesParser(object):
    """
    Warns when there are fewer than one or more than two empty lines
    between contexts.
    """
    def __iter__(self):
        last, blanks = None, 0
        for element in super(EmptyLinesParser, self).__iter__():
            if isinstance(element, EmptyLine):
                if not last:
                    W_CONF_LEADING_EMPTY_LINE(element.where)
                else:
                    blanks += 1
                if blanks == 3:
                    W_CONF_MANY_EMPTY_LINES(element.where)
            elif isinstance(element, Context):
                if last and blanks < 1:
                    W_CONF_FEW_EMPTY_LINES(element.where)
                last, blanks = element, 0
                yield element
            elif isinstance(element, Varset):
                if isinstance(last, Context) and blanks > 0:
                    W_CONF_AN_EMPTY_LINE(element.where)
                elif isinstance(last, Varset) and blanks > 1:
                    W_CONF_MANY_EMPTY_LINES(element.where)
                last, blanks = element, 0
                yield element
            else:
                raise NotImplementedError()


class ConfigInterpreter(EmptyLinesParser, ConfigParser):
    def __iter__(self):
        self.on_begin()

        for element in super(ConfigInterpreter, self).__iter__():
            if isinstance(element, Context):
                self.on_context(element)
            elif isinstance(element, Varset):
                self.on_varset(element)
            else:
                raise NotImplementedError()

        for item in self.on_yield():
            yield item

    def on_begin(self):
        self._contexts = []
        self._curcontext = None

    def on_yield(self):
        for context in self._contexts:
            yield context

    def on_context(self, context):
        # TODO: check for dupes and whatnot?
        # TODO: check for file type specific stuff?
        self._contexts.append(context)
        self._curcontext = context

    def on_varset(self, varset):
        if not self._curcontext:
            E_CONF_MISSING_CTX(varset.where)
        else:
            self._curcontext.add(varset)


class DialplanInterpreter(ConfigInterpreter):
    def on_begin(self):
        self._general = None
        self._globals = None
        self._dialplancontexts = []
        self._curcontext = None

    def on_yield(self):
        if self._general:
            yield self._general
        if self._globals:
            yield self._globals
        for dialplancontext in self._dialplancontexts:
            yield dialplancontext

    def on_context(self, context):
        if context.name == 'general':
            if self._general:
                # Probably more than one [general] works. But it's bad
                # practice.
                # (And the first value will count.)
                E_DP_CONTEXT_DUPE(context.where, self._general.where)
                # Setting curcontext to the original one
                self._curcontext = self._general
            else:
                self._general = context
                self._curcontext = context
        elif context.name == 'globals':
            if self._globals:
                # Only the first [globals] counts.
                E_DP_GLOBALS_DUPE(context.where, self._general.where)
                # Write the rest to the unreferenced one.
                self._curcontext = context
            else:
                self._globals = context
                self._curcontext = context
        else:
            dialplan_context = DialplanContext.from_context(context)
            self.on_dialplancontext(dialplan_context)

    def on_varset(self, varset):
        if not self._curcontext:
            E_CONF_MISSING_CTX(varset.where)
        elif isinstance(self._curcontext, DialplanContext):
            dialplanvarset = DialplanVarset.from_varset(varset)
            self.on_dialplanvarset(dialplanvarset)
        else:
            self._curcontext.add(varset)

    def on_dialplancontext(self, dialplancontext):
        self._dialplancontexts.append(dialplancontext)
        self._curcontext = dialplancontext

    def on_dialplanvarset(self, dialplanvarset):
        assert isinstance(self._curcontext, DialplanContext)
        if isinstance(dialplanvarset, Extension):
            self._curcontext.add(dialplanvarset)
        else:
            raise NotImplementedError()


class FileConfigParser(ConfigInterpreter, FileReader):
    pass


class FileDialplanParser(DialplanInterpreter, FileReader):
    pass


if __name__ == '__main__':
    c = FileDialplanParser(sys.argv[1])
    for context in c:
        # Are we in dialplan? Then parse stuff a bit differently.. by upgrading
        # the Context to a DialplanContext and the Varset to an Extension.
        print(context)
