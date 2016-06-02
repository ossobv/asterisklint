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
import os
import sys
from collections import defaultdict


class MessageDefException(Exception):
    pass


class DuplicateMessageDef(MessageDefException):
    pass


class MessageDefManager(type):
    types = set()
    muted = False
    mute_by_message = set()

    show_line = False
    show_previous = False

    raised = defaultdict(list)

    # The metaclass invocation. (No need for __prepare__ at this
    # point.)
    def __new__(cls, name, bases, classdict):
        class_mute = False

        if name in cls.types:
            raise DuplicateMessageDef(name)
        if not name.endswith('Def'):  # MessageDef, ErrorDef, WarningDef, ...
            cls.types.add(name)       # W_FOO, E_BAR

            # We want the user to specify items to ignore somehow. For
            # now we'll use the environment variable ALINT_IGNORE with a
            # comma delimited list of messages to silence.
            # Example: export ALINT_IGNORE=E_APP_ARG_IFSTYLE,E_FUNC_MISSING,W_
            # (Will silence *all* warnings, through the "W_".)
            alint_ignore = tuple(
                i for i in set(os.environ.get('ALINT_IGNORE', '').split(','))
                if i)
            if name.startswith(alint_ignore):
                for ignore in alint_ignore:
                    if (name == ignore or
                            (ignore[-1] == '_' and
                             name.startswith(ignore))):
                        class_mute = True
                        break

        class_ = type.__new__(cls, name, bases, classdict)

        # Add list of callbacks, specific per class.
        class_._callbacks = []

        # Add class specific mute setting.
        class_.muted = class_mute

        return class_

    @classmethod
    def reset(cls):
        cls.raised = defaultdict(list)

    @classmethod
    def on_message(cls, msg):
        cls.raised[msg.__class__.__name__].append(msg)
        formatted = msg.message.format(**msg.fmtkwargs)

        if cls.muted or msg.muted:
            return

        print('{} {}: {}'.format(
            msg.where, msg.__class__.__name__, formatted),
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
    @classmethod
    def add_callback(cls, callback):
        # self._callbacks is subclass-specific, initialized through our
        # metaclass.
        cls._callbacks.append(callback)

    @classmethod
    def call_callbacks(cls, instance):
        for callback in cls._callbacks:
            callback(instance)

    def __init__(self, where, previous=None, **fmtkwargs):
        self.where = where
        self.previous = previous
        self.fmtkwargs = fmtkwargs
        # Notify optional callbacks.
        self.call_callbacks(self)
        # Notify our general manager.
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
        super().__init__(where, **kwargs)
