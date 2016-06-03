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
from .application import App
from .config import ConfigAggregator, Context, Varset
from .config import E_CONF_CTX_MISSING, E_CONF_KEY_INVALID, W_CONF_CTX_DUPE
from .defines import ErrorDef, WarningDef, HintDef, DupeDefMixin
from .pattern import H_PAT_NON_CANONICAL, Pattern
from .varfun import Var
from .where import Where


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class I_NOTIMPL_HINT(ErrorDef):
        message = 'the dialplan hint directive has not been implemented yet'

    class I_NOTIMPL_IGNOREPAT(ErrorDef):
        message = ('the dialplan ignorepat directive has not been implemented '
                   'yet')

    class I_NOTIMPL_SWITCH(ErrorDef):
        message = 'the dialplan switch directive has not been implemented yet'

    class E_DP_VAR_INVALID(ErrorDef):
        message = ('unexpected variable name {variable!r} '
                   '(not exten/same/include)')

    class E_DP_INCLUDE_POSITION(WarningDef):
        message = 'an include should always be at the tail of the context'

    class E_DP_PAT_INVALID(ErrorDef):
        message = 'badly formatted pattern'

    class E_DP_PAT_MISSING(ErrorDef):
        message = 'missing pattern'

    class E_DP_PRIO_INVALID(ErrorDef):
        message = 'invalid priority {prio!r}'

    class E_DP_PRIO_MISSING(ErrorDef):
        message = 'missing priority'

    class E_DP_PRIO_DUPE(DupeDefMixin, ErrorDef):
        message = 'duplicate priority {prio!r}'

    class E_DP_LABEL_INVALID(ErrorDef):
        message = 'unexpected label value {label!r}'

    class E_DP_GLOBALS_DUPE(DupeDefMixin, ErrorDef):
        message = 'second globals context, will not be used'

    class E_DP_LABEL_DUPE(WarningDef):
        message = 'duplicate label {label!r}, one of them will not be used'

    class E_DP_PRIO_BAD(ErrorDef):
        message = 'cannot match priority for pattern {pat!r}'

    class E_DP_GOTO_CONTEXT_NOLABEL(ErrorDef):
        message = ('label not found in context for goto to {context}, '
                   '{exten}, {label}')

    class E_DP_GOTO_NOCONTEXT(ErrorDef):
        message = 'context not found for goto to {context}, {exten}, {prio}'

    class E_DP_GOTO_NOLABEL(ErrorDef):
        message = ('label not found anywhere for goto to {context}, '
                   '{exten}, {label}')

    class W_DP_GOTO_CONTEXT_NOEXTEN(WarningDef):
        message = ('possibly non-existent extension/pattern for goto to '
                   '{context}, {exten}, {prio}')

    class W_DP_PRIO_BADORDER(WarningDef):
        message = 'bad priority order for pattern {pat!r} and prio {prio}'

    class H_DP_GENERAL_MISPLACED(HintDef):
        message = '[general] context not found or not at top of file'

    class H_DP_GLOBALS_MISPLACED(HintDef):
        message = '[globals] context not found or not at position two'


class Dialplan(object):
    def __init__(self):
        self._general = None
        self._globals = None
        self.contexts = []
        self.contexts_by_name = {}
        self.last_prio = None  # used by the DialplanContext
        self.jump_destinations = []
        self.all_labels = set()  # used when checking jump_destinations

    @property
    def general(self):
        """If it doesn't exist, we return an empty object, so it behaves
        normally."""
        return self._general or DialplanContext('general', dialplan=self)

    @property
    def globals(self):
        """If it doesn't exist, we return an empty object, so it behaves
        normally."""
        return self._globals or DialplanContext('globals', dialplan=self)

    def add_general(self, general):
        if self._general:
            W_CONF_CTX_DUPE(general.where, previous=self._general.where)
            # BEWARE: make sure we use a ref to the NEW context, because
            # we may be appending to that object...!!
            self._general.extend(general)
        else:
            if self._globals or self.contexts:
                H_DP_GENERAL_MISPLACED(general.where)
            self._general = general

    def add_globals(self, globals_):
        if self._globals:
            E_DP_GLOBALS_DUPE(globals_.where, previous=self._globals.where)
            # don't save
        else:
            if not self._general or self.contexts:
                H_DP_GLOBALS_MISPLACED(globals_.where)
            self._globals = globals_

    def has_label(self, label):
        return (label in self.all_labels)

    def get_context(self, name):
        return self.contexts_by_name[name]

    def add_jump_destination(self, context, extension, priority, where):
        self.jump_destinations.append((context, extension, priority, where))

    def walk_jump_destinations(self):
        """
        When the entire dialplan has loaded we can walk over all Goto
        destinations and check for their existence.
        """
        valid_destinations = []

        for context, extension, priority, where in self.jump_destinations:
            if isinstance(context, Var):
                # We won't look up the context if it's build up from a
                # variable. We can however proceed and check whether
                # the label exists.
                if isinstance(priority, str):
                    if not self.has_label(priority):
                        E_DP_GOTO_NOLABEL(
                            where, context=context, exten=extension,
                            label=priority)
            else:
                try:
                    found_context = self.get_context(context)
                except KeyError:
                    E_DP_GOTO_NOCONTEXT(
                        where, context=context, exten=extension, prio=priority)
                else:
                    if isinstance(extension, Var):
                        # We don't look up the extension if it's a
                        # variable (other than EXTEN, which we patched
                        # in before we got here). We can look up the label.
                        if isinstance(priority, str):
                            if not found_context.has_label(priority):
                                E_DP_GOTO_CONTEXT_NOLABEL(
                                    where, context=context, exten=extension,
                                    label=priority)
                    else:
                        found_extension = found_context.match_pattern(
                            extension, priority)
                        if found_extension:
                            valid_destinations.append(found_extension)
                        else:
                            # Exten with prio not found.
                            W_DP_GOTO_CONTEXT_NOEXTEN(
                                where, context=context, exten=extension,
                                prio=priority)

    def get_where(self):
        where = None
        if self.contexts:
            where = Where(
                filename=self.contexts[0].where.filename,
                lineno=0, line='')
        return where

    def on_complete(self):
        if not self._general:
            H_DP_GENERAL_MISPLACED(self.get_where())
        if not self._globals:
            H_DP_GLOBALS_MISPLACED(self.get_where())

    def format_as_dialplan_show(self, reverse=True):
        # Okay; please explain the reverse madness to me? I've seen
        # output from one source in proper order, but usually (Asterisk
        # 13, Asterisk 1.4) it comes in reversed order...
        #
        # Use the `dialplan show` to compare with asterisk output.
        contexts = self.contexts
        if reverse:
            contexts = reversed(contexts)

        ret = []
        for context in contexts:
            ret.append("[ Context {!r} created by 'pbx_config' ]".format(
                context.name))
            last_pattern = None
            for extension in context.by_pattern():
                # NOTE: Asterisk 1.4 and LOW_MEMORY limits show_dialplan
                # output of extension.prio+app_with_parents to 255
                # chars. Asterisk 11 limits it to 1023.
                if extension.pattern == last_pattern:
                    ret.append('     %-14s %-45s [pbx_config]' % (
                        (extension.label and '[{}]'.format(extension.label) or
                            ''),
                        ('%d. %s' % (extension.prio,
                                     extension.app_with_parens))))
                else:
                    last_pattern = extension.pattern
                    ret.append('  %-17s %-45s [pbx_config]' % (
                        "'%s' =>" % (extension.pattern,),
                        ('%d. %s' % (extension.prio,
                                     extension.app_with_parens))))
            for include in context.includes:
                ret.append('  %-17s %-45s [pbx_config]' % (
                    'Include =>', "'%s'" % (include.context_name,)))
            ret.append('')
        return '\n'.join(ret)


class DialplanContext(Context):
    def __init__(self, *args, **kwargs):
        self.dialplan = kwargs.pop('dialplan')
        super().__init__(*args, **kwargs)
        self.includes = []
        self.context_last_prio = None
        self.pattern_cache = {}

    def update(self, othercontext):
        assert not othercontext.includes
        assert othercontext.context_last_prio is None
        self.context_last_prio = None
        super().update(othercontext)

    def by_pattern(self):
        """
        Used by format_as_dialplan_show().
        """
        patterns = sorted(list(set(i.pattern for i in self)))
        ret = []
        for pattern in patterns:
            ret.extend(i for i in self if i.pattern == pattern)
        return ret

    def has_label(self, label):
        """
        Check whether the label is used anywhere in this context.
        """
        return any(label in i['labels'] for i in self.pattern_cache.values())

    def match_pattern(self, extension, priority):
        """
        Find the best matching extension for the priority.
        """
        # FIXME: We should sort once, not always...
        # Sorted patterns.
        patterns = sorted(list(set(i.pattern for i in self)))
        # Matching patterns only.
        for pattern in patterns:
            if pattern.matches_extension(extension):
                extens = [i for i in self if i.pattern == pattern]
                for exten in extens:
                    if isinstance(priority, int):
                        if exten.prio == priority:
                            return exten
                    elif isinstance(priority, str):
                        if exten.label == priority:
                            return exten
                    # Is it a variable? Then format all unknowns as .*
                    # and attempt a regex match.
                    elif (priority.could_match(exten.prio) or
                            priority.could_match(exten.label)):
                        return exten

        # Nothing? Try our includes, but only for integral priorities.
        if isinstance(priority, int):
            for include in self.includes:
                try:
                    context = self.dialplan.get_context(include.context_name)
                except KeyError:
                    # TODO: An include that does not exist. We should
                    # warn about that somewhere else.
                    pass
                else:
                    ret = context.match_pattern(extension, priority)
                    if ret:
                        return ret

        # > If the location that is put into the channel
        # > information is bogus, and asterisk cannot find that
        # > location in the dialplan, then the execution engine
        # > will try to find and execute the code in the
        # > 'i' (invalid) extension in the current context.
        # ...
        # > What this means is that, for example, you specify a
        # > context that does not exist, then it will not be
        # > possible to find the 'h' or 'i' extensions, and the
        # > call will terminate!
        #
        # So, for this context, we can look into 'i' extensions,
        # but we shouldn't look for any if a non-existing context
        # was addressed.
        if extension != 'i':
            # There is no clemency for non-existent labels, only for
            # non-existent priorities.
            if isinstance(priority, int):
                return self.match_pattern('i', 1)

        return None

    def add(self, extension):
        # - If extension.pattern is None ("same") then take previous.
        #   Error if there is none.
        # - If prio is N then assert there is a previous prio with same
        #   pattern.
        if extension.pattern is None:
            if not len(self):
                E_DP_PAT_MISSING(extension.where)
                return None
            extension.pattern = self[-1].pattern

        if extension.prio is None:
            if not self.dialplan.last_prio:
                # Can't use 'next' priority on the first entry at line
                # ..  of extensions.conf!
                E_DP_PRIO_MISSING(
                    extension.where, pat=extension.pattern.raw)
                return
            elif (not self.context_last_prio or
                    self[-1].pattern != extension.pattern):
                W_DP_PRIO_BADORDER(
                    extension.where, pat=extension.pattern.raw,
                    prio='<unset>')
            extension.prio = self.dialplan.last_prio + 1
        elif extension.prio < 1:
            E_DP_PRIO_INVALID(extension.where, prio=extension.prio)
            return
        elif extension.prio != 1:
            # Check that there is a prio with N-1.
            try:
                prev = [i for i in self if i.pattern == extension.pattern][-1]
            except IndexError:
                # TODO: here we have to be careful with pattern
                # matching, we should check whether a pattern exists
                # with a greater scope than our pattern.
                # The odd pattern order can be succesfully employed
                # in temporary branching situations:
                #   _X!,1,both
                #   _1!,2,specific-1-stuff
                #   _[02-9]!,2,specific-other-stuff
                #   _X!,3,both
                W_DP_PRIO_BADORDER(
                    extension.where, pat=extension.pattern.raw,
                    prio=extension.prio)
            else:
                if prev.prio != extension.prio - 1:
                    # Don't warn if same prio, we do the dupe check
                    # later on.
                    if prev.prio != extension.prio:
                        W_DP_PRIO_BADORDER(
                            extension.where, pat=extension.pattern.raw,
                            prio=extension.prio)

        # Okay, prio is valid here. Store it so we can use the next 'n'
        # as last_prio + 1.
        self.dialplan.last_prio = extension.prio
        self.context_last_prio = extension.prio

        # Check pattern cache for duplicates.
        canonical_pattern = extension.pattern.canonical_pattern
        try:
            pattern_cache = self.pattern_cache[canonical_pattern]
        except KeyError:
            pattern_cache = {
                'labels': {},
                'prios': {extension.prio: extension},
            }
            if extension.label:
                pattern_cache['labels'] = {extension.label: extension}
                self.dialplan.all_labels.add(extension.label)
            self.pattern_cache[canonical_pattern] = pattern_cache
        else:
            # Check duplicate priorities.
            previous_with_prio = pattern_cache['prios'].get(extension.prio)
            if previous_with_prio:
                E_DP_PRIO_DUPE(
                    extension.where, previous=previous_with_prio,
                    prio=extension.prio)
                return  # don't insert this one
            pattern_cache['prios'][extension.prio] = extension

            # Check duplicate labels.
            if extension.label:
                previous_with_label = pattern_cache['labels'].get(
                    extension.label)
                if previous_with_label:
                    E_DP_LABEL_DUPE(
                        extension.where, previous=previous_with_label,
                        label=extension.label)
                    extension.label = ''  # wipe it
                else:
                    pattern_cache['labels'][extension.label] = extension
                    self.dialplan.all_labels.add(extension.label)

        # The app may have collected Goto-destinations for us. We must
        # add missing pieces and forward it to a central collector.
        for (g_context, g_exten, g_prio
             ) in extension.app.jump_destinations:
            if not g_context:
                g_context = self.name
            if not g_exten:
                g_exten = extension.pattern.example
            elif isinstance(g_exten, Var):
                try:
                    g_exten = g_exten.format(EXTEN=extension.pattern.example)
                except KeyError:
                    # Never mind.
                    pass
            if isinstance(g_prio, str) and g_prio.isdigit():
                g_prio = int(g_prio)
            self.dialplan.add_jump_destination(
                g_context, g_exten, g_prio, extension.where)

        super().add(extension)

    def add_include(self, include):
        assert isinstance(include, Include)
        # FIXME: check for dupes and other stupidity (circular includes?)
        # FIXME: complain when the include is not at the tail of the context
        self.includes.append(include)


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

            try:
                prio, app = rest.split(',', 1)
            except ValueError:
                prio, app = rest, ''
            try:
                prio, label = prio.split('(', 1)
            except ValueError:
                prio, label = prio, None
            if prio == 'n':
                prio = None
            elif prio.isdigit():
                prio = int(prio)
            elif prio == 'hint':
                I_NOTIMPL_HINT(varset.where)
                return None
            else:
                E_DP_PRIO_INVALID(varset.where, prio=prio)
                return None

            if label is not None:
                if not label.endswith(')'):
                    E_DP_LABEL_INVALID(varset.where)
                    return None
                label = label[0:-1]
                # TODO: check label validity
            else:
                label = None

            pattern = pattern and Pattern(pattern, varset.where) or None
            app = App(app, varset.where)
            return Extension(pattern, prio, label, app, varset.comment,
                             varset.where)

        elif varset.variable == 'include':
            assert varset.arrow  # W_ARROW
            return Include(varset.value, varset.where)

        elif varset.variable == 'switch':
            assert varset.arrow  # W_ARROW
            I_NOTIMPL_SWITCH(varset.where)

        elif varset.variable == 'ignorepat':
            assert varset.arrow  # W_ARROW
            I_NOTIMPL_IGNOREPAT(varset.where)

        else:
            E_CONF_KEY_INVALID(varset.where, key=varset.variable)
            return None


class Include(object):
    def __init__(self, value, where):
        # FIXME: check for value name? contexts existence?
        self.context_name = value
        self.where = where


class Extension(Varset):
    def __init__(self, pattern, prio, label, app, comment, where):
        # Check pattern voor mixen van letters en pattern-letters:
        # - "s-zap" == "s-[1-9]ap" en zou als "s-[z]ap" geschreven moeten
        # - "s-abc" == "sabc"
        # Als pattern is None, dan pakt Context gewoon de vorige, da's
        # prima.
        self.pattern = pattern
        self.prio = prio
        self.label = label
        self.app = app
        self.comment = comment
        self.where = where

    @property
    def app_with_parens(self):
        """
        Used by format_as_dialplan_show().
        """
        ret = [self.app.raw]
        if '(' not in self.app.raw:
            ret.append('(')
        if ')' not in self.app.raw:
            ret.append(')')
        return ''.join(ret)

    @property
    def prio_with_label(self):
        if self.label:
            return '{}({})'.format(self.prio, self.label)
        return str(self.prio)

    def __repr__(self):
        return '<Extension({},{})>'.format(
            self.pattern.raw, self.prio_with_label)


class DialplanAggregator(ConfigAggregator):
    def on_begin(self):
        self._dialplan = Dialplan()
        self._prevcontexts = {}
        self._curcontext = None

    def on_yield(self):
        self._dialplan.on_complete()
        yield self._dialplan

    def on_context(self, context):
        if context.name == 'general':
            self._dialplan.add_general(context)
            self._curcontext = context
        elif context.name == 'globals':
            self._dialplan.add_globals(context)
            self._curcontext = context
        else:
            dialplan_context = DialplanContext.from_context(
                context, dialplan=self._dialplan)
            if dialplan_context:
                self.on_dialplancontext(dialplan_context)

    def on_varset(self, varset):
        if not self._curcontext:
            E_CONF_CTX_MISSING(varset.where)
        elif isinstance(self._curcontext, DialplanContext):
            dialplanvarset = DialplanVarset.from_varset(varset)
            if dialplanvarset:
                self.on_dialplanvarset(dialplanvarset)
        else:
            self._curcontext.add(varset)

    def on_dialplancontext(self, dialplancontext):
        oldcontext = self._prevcontexts.get(dialplancontext.name)
        if oldcontext:
            oldcontext.update(dialplancontext)
            self._curcontext = oldcontext
        else:
            self._prevcontexts[dialplancontext.name] = dialplancontext
            self._dialplan.contexts.append(dialplancontext)
            self._dialplan.contexts_by_name[dialplancontext.name] = (
                dialplancontext)
            self._curcontext = dialplancontext

    def on_dialplanvarset(self, dialplanvarset):
        assert isinstance(self._curcontext, DialplanContext)
        if isinstance(dialplanvarset, Extension):
            pattern = dialplanvarset.pattern
            if pattern and not pattern.is_canonical:
                H_PAT_NON_CANONICAL(
                    dialplanvarset.where, pat=pattern.raw,
                    expected=pattern.canonical_pattern)
            self._curcontext.add(dialplanvarset)
        elif isinstance(dialplanvarset, Include):
            self._curcontext.add_include(dialplanvarset)
        else:
            raise NotImplementedError()
