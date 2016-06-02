# AsteriskLint -- an Asterisk PBX config syntax checker
# Copyright (C) 2015-2016  Walter Doekes, OSSO B.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
import os

from .configobj import EmptyLine, Context, Varset
from .configws import VerticalSpaceWarner
from .defines import ErrorDef, WarningDef, DupeDefMixin
from .file import W_WSH_BOL


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class E_CONF_BAD_LINE(ErrorDef):
        message = 'expected variable = value, line starts with {startswith!r}'

    class E_CONF_CTX_MISSING(ErrorDef):
        message = 'expected context before var/object set'

    class E_CONF_KEY_DUPE(DupeDefMixin, ErrorDef):
        message = 'duplicate varset of {key!r}'

    class E_CONF_KEY_INVALID(ErrorDef):
        message = 'expected valid var/object or new context, got {key!r}'

    class W_CONF_KEY_LATE(WarningDef):
        message = 'expected varset {key!r} earlier, fix your ordering'

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


class ProgrammingError(RuntimeError):
    def __init__(self, message):
        super().__init__(
            'An unexpected exception was raised. This is most likely a '
            'bug in the asterisklint library. If you can reproduce the '
            'problem and file an issue on the bug tracker, that would be '
            'nice. Further info: {}'.format(message))


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
        for where, data, comment in super().__iter__():
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


class ConfigAggregator(VerticalSpaceWarner, ConfigParser):
    def __iter__(self):
        self.on_begin()

        for element in super().__iter__():
            try:
                if isinstance(element, Context):
                    self.on_context(element)
                elif isinstance(element, Varset):
                    self.on_varset(element)
                elif isinstance(element, EmptyLine):
                    self.on_emptyline(element)
                else:
                    raise NotImplementedError()
            except Exception as exc:
                raise ProgrammingError(str(element.where)) from exc

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
