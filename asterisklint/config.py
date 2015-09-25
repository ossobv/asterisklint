# vim: set ts=8 sw=4 sts=4 et ai:
import re
import os

from .defines import ErrorDef, WarningDef, HintDef, DupeDefMixin


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class I_NOTIMPL_TEMPLATES(ErrorDef):
        message = 'asterisklint does not implement template use yet'

    class E_CONF_BAD_LINE(ErrorDef):
        message = 'expected variable = value, line starts with {startswith!r}'

    class E_CONF_CTX_MISSING(ErrorDef):
        message = 'expected context before var/object set'

    class E_CONF_KEY_INVALID(ErrorDef):
        message = 'expected context or var/object set'

    class W_CONF_CTX_DUPE(DupeDefMixin, ErrorDef):
        # BEWARE: chan_pjsip explicitly takes multiple contexts with the
        # same name. But generally it is unwanted and sometimes the
        # values are ignored or the values mask any previously set
        # values.
        message = 'duplicate context found, in some cases it is legal'

    class W_PP_EXEC(WarningDef):
        message = 'using #exec is not recommended; command is {cmd!r}'

    class W_PP_INCLUDE_MISSING(WarningDef):
        message = 'the #include file {filename!r} could not be found'

    class W_PP_QUOTE_BAD(WarningDef):
        message = 'bad quoting near preprocessor directive'

    class W_WSH_CTRL(WarningDef):
        message = 'unexpected non-space/tab whitespace or a mix'

    class W_WSH_BOL(WarningDef):
        message = 'unexpected leading whitespace'

    class W_WSH_OBJSET(WarningDef):
        message = 'expected " => " horizontal whitespace around arrow operator'

    class W_WSH_VARSET(WarningDef):
        message = 'expected no horizontal whitespace around equals operator'

    class W_WSV_BOF(WarningDef):
        message = 'unexpected vertical space at beginning of file'

    class W_WSV_EOF(WarningDef):
        message = 'unexpected vertical space at end of file'

    class H_WSV_CTX_BETWEEN(HintDef):
        message = 'expected one or two lines between contexts'

    class H_WSV_VARSET_BETWEEN(HintDef):
        message = 'expected zero or one lines between varsets'


class EmptyLine(object):
    def __init__(self, comment, where):
        self.comment = comment
        self.where = where


class Context(object):
    @classmethod
    def from_context(cls, context):
        """
        Use this on subclasses of Context.
        """
        assert not context._varsets
        return cls(context.name, context._templates, context.comment,
                   context.where)

    def __init__(self, name, templates, comment, where):
        self.name = name
        self.comment = comment
        self.where = where
        self._templates = templates
        self._varsets = []

        if templates:
            I_NOTIMPL_TEMPLATES(where)

    def add(self, varset):
        self._varsets.append(varset)

    def __bool__(self):
        # Must(!) define this, now that we use __len__.
        return True

    def __len__(self):
        return len(self._varsets)

    def __getitem__(self, key):
        assert isinstance(key, int)
        return self._varsets[key]

    def __repr__(self):
        return '[{}]({}) => ({} elements)'.format(
            self.name, self._templates, len(self._varsets))


class Varset(object):
    def __init__(self, variable, value, separator, comment, where):
        clean_separator = separator.strip()
        if clean_separator == '=>':
            if separator != ' => ':
                W_WSH_OBJSET(where)
            self.arrow = True
        elif clean_separator == '=':
            if separator != '=':
                W_WSH_VARSET(where)
            self.arrow = False

        if variable.startswith(tuple(' \t')):
            # QUICK HACK: only allow leading WS for 'same'..
            variable = variable.lstrip(' \t')
            if variable != 'same':
                W_WSH_BOL(where)

        self.variable = variable
        self.value = value
        self.comment = comment
        self.where = where


class ConfigParser(object):
    # Parse config and emit 1=>X
    # Define who prefers "=>" and who prefers "=". Allow warnings about
    # that to be disabled.
    # Allow templating? Feature v1.1.

    # TODO: compain about too much and/or too little white space!

    # TODO: look at: main/config.c: process_text_line()
    # it will show odd escaping, and multiline stuff
    # TODO: include/tryinclude/exec

    regexes = (
        # [context](template1,template2)
        (re.compile(r'^\[([^]]*)\]\s*\(([^)\+])\)$'),
         (lambda comment, where, match: Context(
             name=match.groups()[0], templates=match.groups()[1],
             comment=comment, where=where))),
        # [context]
        (re.compile(r'^\[([^]]*)\]$'),
         (lambda comment, where, match: Context(
             name=match.groups()[0], templates='',
             comment=comment, where=where))),
        # object => value
        (re.compile(r'^([^=]*?)(\s*=>\s*)(.*)$'),
         (lambda comment, where, match: Varset(
             variable=match.groups()[0], value=match.groups()[2],
             separator=match.groups()[1], comment=comment, where=where))),
        # variable = value
        (re.compile(r'^([^=]*?)(\s*=\s*)(.*)$'),
         (lambda comment, where, match: Varset(
             variable=match.groups()[0], value=match.groups()[2],
             separator=match.groups()[1], comment=comment, where=where))),
        # (void)
        (re.compile(r'^\s*$'),
         (lambda comment, where, match: EmptyLine(
             comment=comment, where=where))),
    )

    def __iter__(self):
        for where, data, comment in super(ConfigParser, self).__iter__():
            for regex, func in self.regexes:
                match = regex.match(data)
                if match:
                    # Cast the comment to a boolean, we're not using the
                    # contents, ever.
                    value = func(bool(comment), where, match)
                    yield value
                    break
            else:
                if data.startswith('#'):
                    # Call the preprocessor, it may insert data into our
                    # internal data generator.
                    self.preprocessor(where, data, bool(comment))
                else:
                    E_CONF_BAD_LINE(where, startswith=data[0:16])

    def preprocessor(self, where, data, comment):
        if data.startswith('#include'):
            cmd, rest = data[0:8], data[8:]
        elif data.startswith('#tryinclude'):
            cmd, rest = data[0:11], data[11:]
        elif data.startswith('#exec'):
            cmd, rest = data[0:5], data[5:]
        else:
            rest = None

        if not rest or ord(rest[0]) > 32:
            E_CONF_BAD_LINE(where, startswith=data[0:16])
            return

        for idx, ch in enumerate(rest):
            if ord(ch) > 32:
                break
        else:
            # Nothing after the #include/#tryinclude/#exec.
            E_CONF_BAD_LINE(where, startswith=data[0:16])
            return

        if (not all(i == ' ' for i in rest[0:idx]) and
                not all(i == '\t' for i in rest[0:idx])):
            W_WSH_CTRL(where)
        rest = rest[idx:]

        if rest[0] == '"' and rest[-1] == '"':
            rest = rest[1:-1]
        elif rest[0] == '<' and rest[-1] == '>':
            rest = rest[1:-1]
        elif (rest[0] == '<' or rest[0] == '"' or rest[-1] == '"' or
                rest[-1] == '>'):
            W_PP_QUOTE_BAD(where)

        # Very well. Let's rock.
        if cmd == '#exec':
            W_PP_EXEC(where, cmd=rest)
        elif cmd in ('#include', '#tryinclude'):
            error_if_not_exists = (cmd == '#include')
            try:
                self.include(os.path.join(os.path.dirname(where.filename),
                                          rest))
            except OSError:
                if error_if_not_exists:
                    W_PP_INCLUDE_MISSING(where, filename=rest)


class EmptyLinesParser(object):
    """
    Warns when there are fewer than one or more than two empty lines
    between contexts.
    """
    def __iter__(self):
        last = None
        buffer_ = []
        for element in super(EmptyLinesParser, self).__iter__():
            if isinstance(element, EmptyLine) and not element.comment:
                buffer_.append(element)

            else:
                if not last:
                    if len(buffer_):
                        W_WSV_BOF(element.where)
                elif (isinstance(element, Context) and
                        len(buffer_) not in (1, 2)):
                    H_WSV_CTX_BETWEEN(element.where)
                elif (isinstance(element, Varset) and
                        len(buffer_) > 1):
                    H_WSV_VARSET_BETWEEN(element.where)

                for old in buffer_:
                    yield old
                buffer_ = []
                last = element
                yield element

        if buffer_:
            W_WSV_EOF(element.where)
            for old in buffer_:
                yield old


class ConfigAggregator(EmptyLinesParser, ConfigParser):
    def __iter__(self):
        self.on_begin()

        for element in super(ConfigAggregator, self).__iter__():
            if isinstance(element, Context):
                self.on_context(element)
            elif isinstance(element, Varset):
                self.on_varset(element)
            elif isinstance(element, EmptyLine):
                self.on_emptyline(element)
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
            E_CONF_CTX_MISSING(varset.where)
        else:
            self._curcontext.add(varset)

    def on_emptyline(self, emptyline):
        # We don't want these.
        pass
