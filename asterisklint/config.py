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
        return cls(name=context.name, templates=context._templates,
                   comment=context.comment, bolspace='',
                   where=context.where)

    def __init__(self, name, templates='', comment=False, bolspace='',
                 where=None):
        if bolspace:
            W_WSH_BOL(where)

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

    # TODO: look at: main/config.c: process_text_line()
    # it will show odd escaping, and multiline stuff

    regexes = (
        # [context](template1,template2)
        (re.compile(r'^(\s*)\[([^]]*)\]\s*\(([^)\+])\)$'),
         (lambda comment, where, match: Context(
             name=match.groups()[1], templates=match.groups()[2],
             comment=comment, bolspace=match.groups()[0], where=where))),
        # [context]
        (re.compile(r'^(\s*)\[([^]]*)\]$'),
         (lambda comment, where, match: Context(
             name=match.groups()[1], templates='',
             comment=comment, bolspace=match.groups()[0], where=where))),
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
                if data.lstrip().startswith('#'):
                    # Call the preprocessor, it may insert data into our
                    # internal data generator.
                    self.preprocessor(where, data, bool(comment))
                else:
                    E_CONF_BAD_LINE(where, startswith=data[0:16])

    def preprocessor(self, where, data, comment):
        text = data.lstrip()
        leading = data[0:(len(data) - len(text))]
        if leading:
            W_WSH_BOL(where)

        if text.startswith('#include'):
            cmd, rest = text[0:8], text[8:]
        elif text.startswith('#tryinclude'):
            cmd, rest = text[0:11], text[11:]
        elif text.startswith('#exec'):
            cmd, rest = text[0:5], text[5:]
        else:
            rest = None

        if not rest or ord(rest[0]) > 32:
            E_CONF_BAD_LINE(where, startswith=text[0:16])
            return

        for idx, ch in enumerate(rest):
            if ord(ch) > 32:
                break
        else:
            # Nothing after the #include/#tryinclude/#exec.
            E_CONF_BAD_LINE(where, startswith=text[0:16])
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


class VerticalSpaceWarner(object):
    """
    Warns about irregular vertical whitespace (WSV).

    Contexts get one or two leading white lines. Varsets get at most one
    leading white line.

    OBSERVE: This doesn't take preprocessor includes into account now:
    #included files will not get W_WSV_EOF warnings.
    """
    def __iter__(self):
        last_non_blank = None
        blanks = []

        for element in super().__iter__():
            if isinstance(element, EmptyLine):
                blanks.append(element)

            else:
                if not last_non_blank:
                    if blanks and not blanks[0].comment:
                        min_blanks, max_blanks = 0, 2
                    else:
                        min_blanks, max_blanks = 0, 0
                    message = H_WSV_CTX_BETWEEN
                elif isinstance(element, Context):
                    min_blanks, max_blanks = 1, 2
                    message = H_WSV_CTX_BETWEEN
                elif isinstance(element, Varset):
                    min_blanks, max_blanks = 0, 1
                    message = H_WSV_VARSET_BETWEEN
                else:
                    raise NotImplementedError('unknown element {!r}'.format(
                        element))

                # Check minvalues first.
                if len(blanks) < min_blanks:
                    message(element.where)
                    for blank in blanks:
                        yield blank
                elif not blanks:
                    pass
                else:
                    # Group the blanks by comment/non-comment.
                    grouped = self.group_blanks(blanks)
                    if not last_non_blank:
                        if not grouped[0][0]:
                            W_WSV_BOF(grouped[0][1][0].where)
                            has_comment, grouped_blanks = grouped.pop(0)
                            for blank in grouped_blanks:
                                yield blank
                    for i, (has_comment, grouped_blanks) in enumerate(grouped):
                        if (not has_comment and
                                len(grouped_blanks) > max_blanks):
                            message(grouped_blanks[-1].where)
                        # Yield it all.
                        for blank in grouped_blanks:
                            yield blank

                blanks = []
                last_non_blank = element
                yield element

        if blanks:
            # Group any leftover blanks by comment/non-comment.
            message = H_WSV_CTX_BETWEEN
            max_blanks = 2
            grouped = self.group_blanks(blanks)

            # Save the tail for the EOF warning.
            if not grouped[-1][0]:
                eof_blanks = grouped.pop()[1]
            else:
                eof_blanks = []

            # Process the rest.
            for has_comment, grouped_blanks in grouped:
                if (not has_comment and
                        len(grouped_blanks) > max_blanks):
                    message(grouped_blanks[-1].where)
                # Yield it all.
                for blank in grouped_blanks:
                    yield blank

            # Check tail whitespace and report on that.
            if eof_blanks:
                for blank in eof_blanks:
                    yield blank
                W_WSV_EOF(blanks[-1].where)

    def group_blanks(self, blanks):
        ret = []
        for blank in blanks:
            if ret and ret[-1][0] == bool(blank.comment):
                ret[-1][1].append(blank)
            else:
                ret.append((bool(blank.comment), [blank]))
        return ret


class ConfigAggregator(VerticalSpaceWarner, ConfigParser):
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
