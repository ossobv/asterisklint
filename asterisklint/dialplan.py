# vim: set ts=8 sw=4 sts=4 et ai:
from .config import ConfigAggregator, Context, Varset
from .config import E_CONF_MISSING_CTX
from .defines import ErrorDef, WarningDef


if 'we_dont_want_two_linefeeds_between_classdefs':  # for flake8
    class I_NOTIMPL_HINT(ErrorDef):
        message = 'the dialplan hint directive has not been implemented yet'

    class I_NOTIMPL_INCLUDE(ErrorDef):
        message = 'the dialplan include directive has not been implemented yet'

    class E_DP_VAR_INVALID(ErrorDef):
        message = 'unexpected variable name (not exten/same/include)'

    class E_DP_PAT_INVALID(ErrorDef):
        message = 'badly formatted pattern'

    class E_DP_PAT_MISSING(ErrorDef):
        message = 'missing pattern'

    class E_DP_PRIO_INVALID(ErrorDef):
        message = 'invalid priority'

    class E_DP_PRIO_MISSING(ErrorDef):
        message = 'missing priority'

    class E_DP_PRIO_DUPE(ErrorDef):
        message = 'duplicate priority'

    class E_DP_LABEL_INVALID(ErrorDef):
        message = 'unexpected label value'

    class E_DP_GLOBALS_DUPE(ErrorDef):
        message = 'second globals context, will not be used'

    class W_DP_CONTEXT_DUPE(WarningDef):
        message = 'duplicate context, not an error, but not nice'

    class W_DP_LABEL_DUPE(WarningDef):
        message = 'duplicate label'

    class W_DP_PRIO_BADORDER(ErrorDef):
        message = 'bad priority order'


class Dialplan(object):
    def __init__(self):
        self._general = None
        self._globals = None
        self.contexts = []

    @property
    def general(self):
        """If it doesn't exist, we return an empty object, so it behaves
        normally."""
        return self._general or DialplanContext(
            'general', templates='', comment=False, where=None)

    @property
    def globals(self):
        """If it doesn't exist, we return an empty object, so it behaves
        normally."""
        return self._globals or DialplanContext(
            'globals', templates='', comment=False, where=None)

    def add_general(self, general):
        if self._general:
            W_DP_CONTEXT_DUPE(general.where, self._general.where)
            # BEWARE: make sure we use a ref to the NEW context, because
            # we may be appending to that object...!!
            self._general.extend(general)
        else:
            self._general = general

    def add_globals(self, globals_):
        if self._globals:
            E_DP_GLOBALS_DUPE(globals_.where, self._globals.where)
            # don't save
        else:
            self._globals = globals_

    def format_as_dialplan_show(self):
        # If we have this, we can compare to the asterisk output :)
        ret = []
        for context in reversed(self.contexts):
            ret.append("[ Context {!r} created by 'pbx_config' ]".format(
                context.name))
            # TODO: context.by_pattern? print the "=>" notation for the
            # first of every pattern. note that the show-dialplan is
            # ordered by pattern..
            last_pattern = None
            for extension in context.by_pattern():
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
            ret.append('')
        return '\n'.join(ret)


class DialplanContext(Context):
    def by_pattern(self):
        """
        Used by format_as_dialplan_show().
        """
        patterns = list(set(i.pattern for i in self))  # TODO: order
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
            if not len(self):
                E_DP_PRIO_MISSING(extension.where)
                return
            if self[-1].pattern != extension.pattern:
                W_DP_PRIO_BADORDER(extension.where)
                prev = [i for i in self if i.pattern == extension.pattern][-1]
            else:
                prev = self[-1]
            assert prev.pattern == extension.pattern  # E_PRIO_FUCKUP
            extension.prio = prev.prio + 1
        elif extension.prio < 1:
            E_DP_PRIO_INVALID(extension.where)
            return
        elif extension.prio != 1:
            # Check that there is a prio with N-1.
            # TODO: here we have to be careful with pattern matching, we
            # should check whether a pattern exists with a greater scope
            # than our pattern.
            try:
                prev = [i for i in self if i.pattern == extension.pattern][-1]
            except IndexError:
                W_DP_PRIO_BADORDER(extension.where)
            else:
                if prev.prio != extension.prio - 1:
                    # Don't warn if same prio, we do the dupe check
                    # later on.
                    if prev.prio != extension.prio:
                        W_DP_PRIO_BADORDER(extension.where)

        # Check duplicate priorities.
        extensions = [i for i in self if i.pattern == extension.pattern]
        if extension.prio in [i.prio for i in extensions]:
            E_DP_PRIO_DUPE(extension.where)
            return

        # Check duplicate labels.
        if (extension.label and
                extension.label in [i.label for i in extensions]):
            W_DP_LABEL_DUPE(extension.where)
            extension.label = ''  # wipe it

        super(DialplanContext, self).add(extension)


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
            elif prio == 'hint':
                I_NOTIMPL_HINT(varset.where)
                return None
            else:
                E_DP_PRIO_INVALID(varset.where)
                return None

            if label is not None:
                if not label.endswith(')'):
                    E_DP_LABEL_INVALID(varset.where)
                    return None
                label = label[0:-1]
                # TODO: check label validity
            else:
                label = None

            return Extension(pattern, prio, label, app, varset.comment,
                             varset.where)

        elif varset.variable == 'include':
            assert varset.arrow  # W_ARROW
            return Include(varset.value, varset.where)

        else:
            E_DP_VAR_INVALID(varset.where)
            return None


class Include(object):
    # FIXME
    def __init__(self, value, where):
        self.where = where
        pass


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
        ret = [self.app]
        if '(' not in self.app:
            ret.append('(')
        if ')' not in self.app:
            ret.append(')')
        return ''.join(ret)


class DialplanAggregator(ConfigAggregator):
    def on_begin(self):
        self._dialplan = Dialplan()
        self._curcontext = None

    def on_yield(self):
        yield self._dialplan

    def on_context(self, context):
        if context.name == 'general':
            self._dialplan.add_general(context)
            self._curcontext = context
        elif context.name == 'globals':
            self._dialplan.add_globals(context)
            self._curcontext = context
        else:
            dialplan_context = DialplanContext.from_context(context)
            if dialplan_context:
                self.on_dialplancontext(dialplan_context)

    def on_varset(self, varset):
        if not self._curcontext:
            E_CONF_MISSING_CTX(varset.where)
        elif isinstance(self._curcontext, DialplanContext):
            dialplanvarset = DialplanVarset.from_varset(varset)
            if dialplanvarset:
                self.on_dialplanvarset(dialplanvarset)
        else:
            self._curcontext.add(varset)

    def on_dialplancontext(self, dialplancontext):
        self._dialplan.contexts.append(dialplancontext)
        self._curcontext = dialplancontext

    def on_dialplanvarset(self, dialplanvarset):
        assert isinstance(self._curcontext, DialplanContext)
        if isinstance(dialplanvarset, Extension):
            self._curcontext.add(dialplanvarset)
        elif isinstance(dialplanvarset, Include):
            I_NOTIMPL_INCLUDE(dialplanvarset.where)
        else:
            raise NotImplementedError()
