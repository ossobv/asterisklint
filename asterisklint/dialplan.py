# vim: set ts=8 sw=4 sts=4 et ai:
from .config import ConfigAggregator, Context, Varset
from .defines import ErrorDef, WarningDef


if True:
    class E_DP_BAD_VALUE(ErrorDef):
        message = 'unexpected varset (not exten/same/include)'

    class E_DP_BAD_PRIO(ErrorDef):
        message = 'unexpected priority value'

    class E_DP_BAD_LABEL(ErrorDef):
        message = 'unexpected label value'

    class E_DP_GLOBALS_DUPE(ErrorDef):
        message = 'second globals context, will not be used'

    class W_DP_CONTEXT_DUPE(WarningDef):
        message = 'duplicate context, not an error, but not nice'


class Dialplan(object):
    def __init__(self):
        self.general = None
        self.globals = None
        self.contexts = []

    def add_general(self, general):
        if self.general:
            W_DP_CONTEXT_DUPE(general.where, self.general.where)
            # BEWARE: make sure we use a ref to the NEW context, because
            # we may be appending to that object...!!
            self.general.extend(general)
        else:
            self.general = general

    def add_globals(self, globals_):
        if self.globals:
            E_DP_GLOBALS_DUPE(globals_.where, self.globals.where)
            # don't save
        else:
            self.globals = globals_

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
                        "'%s' =>" % (extension.pattern_with_label,),
                        ('%d. %s' % (extension.prio,
                                     extension.app_with_parens))))
            ret.append('')
        return '\n'.join(ret)


class DialplanContext(Context):
    def by_pattern(self):
        """
        Used by format_as_dialplan_show().
        """
        patterns = list(set(i.pattern for i in self.varsets))  # TODO: order
        ret = []
        for pattern in patterns:
            ret.extend(i for i in self.varsets if i.pattern == pattern)
        return ret

    def add(self, extension):
        # - If extension.pattern is None ("same") then take previous.
        #   Error if there is none.
        # - If prio is N then assert there is a previous prio with same
        #   pattern.
        self.varsets.append(extension)


class DialplanVarset(object):
    @classmethod
    def from_varset(cls, varset, context):
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
                    E_DP_BAD_LABEL(varset.where)
                    return None
                label = label[0:-1]
                # TODO: check label validity
            else:
                label = None

            return Extension(context, pattern, prio, label, app, varset.where)

        elif varset.variable == 'include':
            assert varset.arrow  # W_ARROW
            return Include(varset.value, varset.where)

        else:
            E_DP_BAD_VALUE(varset.where)
            return None


class Include(object):
    # FIXME
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
    def __init__(self, context, pattern, prio, label, app, where):
        # Check pattern voor mixen van letters en pattern-letters:
        # - "s-zap" == "s-[1-9]ap" en zou als "s-[z]ap" geschreven moeten
        # - "s-abc" == "sabc"
        # Als pattern is None, dan pakt Context gewoon de vorige, da's
        # prima.
        if pattern is None:
            pattern = context.varsets[-1].pattern
        self.pattern = pattern

        if prio is None:
            prev = context.varsets[-1]
            assert prev.pattern == pattern  # E_PRIO_FUCKUP
            prio = prev.prio + 1
        self.prio = prio

        self.label = label  # TODO: check labels
        self.app = app
        self.where = where

    @property
    def pattern_with_label(self):
        """
        Used by format_as_dialplan_show().
        """
        if self.label is None:
            return self.pattern
        return '%s(%s)' % (self.pattern, self.label)

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
            self.on_dialplancontext(dialplan_context)

    def on_varset(self, varset):
        if isinstance(self._curcontext, DialplanContext):
            dialplanvarset = DialplanVarset.from_varset(
                varset, self._curcontext)
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
        else:
            raise NotImplementedError()
