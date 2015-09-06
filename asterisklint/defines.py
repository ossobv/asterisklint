# vim: set ts=8 sw=4 sts=4 et ai:
from collections import defaultdict


class MessageDefException(Exception):
    pass


class DuplicateMessageDef(MessageDefException):
    pass


class MessageDefManager(type):
    types = set()
    raised = defaultdict(list)

    # The metaclass invocation. (No need for __prepare__ at this
    # point.)
    def __new__(cls, name, bases, classdict):
        if name in cls.types:
            raise DuplicateMessageDef(name)
        cls.types.add(name)
        return type.__new__(cls, name, bases, classdict)

    @classmethod
    def on_message(cls, msg):
        cls.raised[msg.__class__.__name__].append(msg)
        print('( raised:', dict((k, len(v)) for k, v in cls.raised.items()),
              ')')

        print('{} {}: {}'.format(
            msg.where, msg.__class__.__name__, msg.message))

        if msg.previous:
            print('  see previous: {}'.format(msg.previous))

        line_repr = repr(msg.where.line)
        if len(line_repr) > 64:
            line_repr = line_repr[1:64] + '...'  # drop "b", trim to 63
        else:
            line_repr = line_repr[1:]  # drop "b"
        print('  => {}'.format(line_repr))


class MessageDef(object, metaclass=MessageDefManager):
    def __init__(self, where, previous=None):
        self.where = where
        self.previous = previous
        MessageDefManager.on_message(self)


class ErrorDef(MessageDef):
    pass


class WarningDef(MessageDef):
    pass
