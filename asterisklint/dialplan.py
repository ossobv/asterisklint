# vim: set ts=8 sw=4 sts=4 et ai:
from .application import App
from .config import ConfigAggregator, Context, Varset
from .config import E_CONF_CTX_MISSING, E_CONF_KEY_INVALID, W_CONF_CTX_DUPE
from .defines import ErrorDef, WarningDef, HintDef, DupeDefMixin
from .pattern import H_PAT_NON_CANONICAL, Pattern
from .where import Where


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class I_NOTIMPL_HINT(ErrorDef):
        message = 'the dialplan hint directive has not been implemented yet'

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
        self.last_prio = None  # used by the DialplanContext

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

        # Check duplicate priorities.
        extensions = [i for i in self if i.pattern == extension.pattern]
        if any(i.prio == extension.prio for i in extensions):
            previous = [i.where for i in extensions
                        if i.prio == extension.prio][0]
            E_DP_PRIO_DUPE(
                extension.where, previous=previous, prio=extension.prio)
            return

        # Check duplicate labels.
        if (extension.label and
                any(True for i in extensions if i.label == extension.label)):
            previous = [i.where for i in extensions
                        if i.label == extensions.label][0]
            E_DP_LABEL_DUPE(extension.where, previous=previous)
            extension.label = ''  # wipe it

        super(DialplanContext, self).add(extension)

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

        else:
            E_CONF_KEY_INVALID(varset.where)
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
