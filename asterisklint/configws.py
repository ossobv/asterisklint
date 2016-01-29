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
from .configobj import EmptyLine, Context, Varset
from .defines import HintDef
from .file import W_WSV_BOF, W_WSV_EOF


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class H_WSV_CTX_BETWEEN(HintDef):
        # We skip this if the context contains only 0..2 varsets.
        message = 'expected one or two lines between non-tiny contexts'

    class H_WSV_VARSET_BETWEEN(HintDef):
        message = 'expected zero or one lines between varsets'


class VswContext(object):
    """
    We need a separate context object to keep state per file. Because of
    how the parser works, we won't get any notifications about file
    switches, other than that the "where" changes. This VswContext and
    the VswContextStack keep track of the changes and of the
    file-specific state.
    """
    def __init__(self, where):
        self.filename = where.filename
        self.bof = True
        self.blanks = []
        self.last_context_varsets = 0

    def is_where(self, where):
        return self.filename == where.filename

    def handle(self, element):
        if isinstance(element, EmptyLine):
            self.blanks.append(element)
        else:
            for delayed in self.handle_nonblank(element):
                yield delayed

    def handle_nonblank(self, element):
        if isinstance(element, Context):
            if self.last_context_varsets <= 2:
                min_blanks = 0
            else:
                min_blanks = 1
            max_blanks = 2
            message = H_WSV_CTX_BETWEEN
            self.last_context_varsets = 0
        elif isinstance(element, Varset):
            min_blanks, max_blanks = 0, 1
            message = H_WSV_VARSET_BETWEEN
            self.last_context_varsets += 1
        else:
            raise NotImplementedError('unknown element {!r}'.format(
                element))

        for blank in self.flush_blanks(element, message, min_blanks,
                                       max_blanks):
            yield blank

        self.bof = False  # after flush_blanks..
        yield element

    def flush_blanks(self, element, message, min_blanks, max_blanks):
        # Check minvalues first.
        if len(self.blanks) < min_blanks:
            message(element.where)
            for blank in self.blanks:
                yield blank
            self.blanks = []
            return

        # Nothing to do?
        if not self.blanks:
            return

        # Group the blanks by comment/non-comment. From the
        # non-comments we only want to see max_blanks in a row.
        grouped = self.group_blanks(self.blanks)
        if self.bof:
            if not grouped[0][0]:
                W_WSV_BOF(grouped[0][1][0].where)
                has_comment, grouped_blanks = grouped.pop(0)
                for blank in grouped_blanks:
                    yield blank
        for i, (has_comment, grouped_blanks) in enumerate(grouped):
            if (not has_comment and
                    len(grouped_blanks) > max_blanks):
                message(grouped_blanks[-1].where)
            for blank in grouped_blanks:
                yield blank
        self.blanks = []

    def handle_eof(self, report_eof_blanks=True):
        if not self.blanks:
            return

        # Group any leftover blanks by comment/non-comment.
        message = H_WSV_CTX_BETWEEN
        max_blanks = 2
        grouped = self.group_blanks(self.blanks)

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
        if eof_blanks and report_eof_blanks:
            for blank in eof_blanks:
                yield blank
            W_WSV_EOF(self.blanks[-1].where)

    def group_blanks(self, blanks):
        ret = []
        for blank in blanks:
            if ret and ret[-1][0] == bool(blank.comment):
                ret[-1][1].append(blank)
            else:
                ret.append((bool(blank.comment), [blank]))
        return ret


class VswContextStack(list):
    def handle(self, element):
        if not self.is_on_stack(element.where):
            self.append(VswContext(element.where))
        else:
            while not self[-1].is_where(element.where):
                locontext = self.pop()
                for delayed in locontext.handle_eof():
                    yield delayed
            assert self, 'eof of last file will not happen here'

        for delayed in self[-1].handle(element):
            yield delayed

    def is_on_stack(self, where):
        return any(i.is_where(where) for i in reversed(self))

    def handle_eof(self):
        first = True
        while self:
            locontext = self.pop()
            for delayed in locontext.handle_eof(report_eof_blanks=first):
                yield delayed
            first = False


class VerticalSpaceWarner(object):
    """
    Warns about irregular vertical whitespace (WSV).

    Contexts get one or two leading white lines. Varsets get at most one
    leading white line.
    """
    def __iter__(self):
        # We use a VswContext object to keep state per "included" file.
        # Every time a file include changes, we push/pop the context
        # stack.
        stack = VswContextStack()
        for element in super().__iter__():
            for delayed in stack.handle(element):
                yield delayed
        for delayed in stack.handle_eof():
            yield delayed
