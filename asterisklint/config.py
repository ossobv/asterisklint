# vim: set ts=8 sw=4 sts=4 et ai:
import re

from .defines import ErrorDef, WarningDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class I_NOTIMPL_TEMPLATES(ErrorDef):
        message = 'asterisklint does not implement template use yet'

    class E_CONF_BAD_LINE(ErrorDef):
        message = 'expected variable = value'

    class E_CONF_NOCTX_NOVAR(ErrorDef):
        message = 'expected context or var/object set'

    class E_CONF_MISSING_CTX(ErrorDef):
        message = 'expected context before var/object set'

    class W_CONF_LEADING_EMPTY_LINE(WarningDef):
        message = 'leading empty lines are not pretty'

    class W_CONF_MANY_EMPTY_LINES(WarningDef):
        message = 'excess blank lines'

    class W_CONF_FEW_EMPTY_LINES(WarningDef):
        message = 'too few empty lines'

    class W_CONF_AN_EMPTY_LINE(WarningDef):
        message = 'unexpected empty line'

    class W_WSH_BOL(WarningDef):
        message = 'unexpected leading whitespace'

    class W_WSH_OBJSET(WarningDef):
        message = 'expected " => " horizontal whitespace around arrow operator'

    class W_WSH_VARSET(WarningDef):
        message = 'expected no horizontal whitespace around equals operator'


class EmptyLine(object):
    def __init__(self, where):
        self.where = where


class Context(object):
    @classmethod
    def from_context(cls, context):
        """
        Use this on subclasses of Context.
        """
        assert not context._varsets
        return cls(context.name, context._templates, context.where)

    def __init__(self, name, templates, where):
        self.name = name
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
    def __init__(self, variable, value, separator, where):
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
        self.where = where


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
        (re.compile(r'^([^=]*?)(\s*=>\s*)(.*)$'),
         (lambda where, match: Varset(
             variable=match.groups()[0], value=match.groups()[2],
             separator=match.groups()[1], where=where))),
        # variable = value
        (re.compile(r'^([^=]*?)(\s*=\s*)(.*)$'),
         (lambda where, match: Varset(
             variable=match.groups()[0], value=match.groups()[2],
             separator=match.groups()[1], where=where))),
        # (void)
        (re.compile(r'^\s*$'),
         (lambda where, match: EmptyLine(where=where))),
    )

    def __iter__(self):
        for where, data, comment in super(ConfigParser, self).__iter__():
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


class ConfigAggregator(EmptyLinesParser, ConfigParser):
    def __iter__(self):
        self.on_begin()

        for element in super(ConfigAggregator, self).__iter__():
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
