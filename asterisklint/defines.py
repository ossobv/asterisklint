# vim: set ts=8 sw=4 sts=4 et ai:
import sys
from collections import defaultdict


class MessageDefException(Exception):
    pass


class DuplicateMessageDef(MessageDefException):
    pass


class MessageDefManager(type):
    types = set()
    muted = False

    show_line = False
    show_previous = False

    raised = defaultdict(list)

    # The metaclass invocation. (No need for __prepare__ at this
    # point.)
    def __new__(cls, name, bases, classdict):
        if name in cls.types:
            raise DuplicateMessageDef(name)
        if not name.endswith('Def'):  # MessageDef, ErrorDef, WarningDef, ...
            cls.types.add(name)       # W_FOO, E_BAR
        return type.__new__(cls, name, bases, classdict)

    @classmethod
    def reset(cls):
        cls.raised = defaultdict(list)

    @classmethod
    def on_message(cls, msg):
        cls.raised[msg.__class__.__name__].append(msg)

        if cls.muted:
            return

        print('{} {}: {}'.format(
            msg.where, msg.__class__.__name__, msg.message),
            file=sys.stderr)

        if cls.show_line:
            line_repr = repr(msg.where.line)
            if len(line_repr) > 64:
                line_repr = line_repr[1:64] + '...'  # drop "b", trim to 63
            else:
                line_repr = line_repr[1:]  # drop "b"
            print('  => {}'.format(line_repr), file=sys.stderr)

        if cls.show_previous and msg.previous:
            print(
                '    previous occurrence at {}'.format(msg.previous),
                file=sys.stderr)


class MessageDef(object, metaclass=MessageDefManager):
    def __init__(self, where, previous=None, notes=None):
        self.where = where
        self.previous = previous
        self.notes = notes  # TODO: use this for hints
        MessageDefManager.on_message(self)


class ErrorDef(MessageDef):
    pass


class WarningDef(MessageDef):
    pass


class HintDef(MessageDef):
    pass


class DupeDefMixin(object):
    def __init__(self, where, **kwargs):
        if not kwargs.get('previous'):
            raise TypeError("{} requires a ``previous'' argument".format(
                self.__class__.__name__))
        super(DupeDefMixin, self).__init__(where, **kwargs)
