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


class Singleton(type):
    """
    Create singleton classes. Usage::

        class MyClass(metaclass=Singleton):
            ...

        MyClass().do_stuff()

    If your class implements the reinit() method, it will be called with
    the same arguments as to __init__ in case it was already created.
    There you may evaluate if the args/kwargs are allowed and/or need
    updating::

        def reinit(self, optional_config=None):
            if optional_config and self.config != optional_config:
                raise ProgrammingError("You cannot switch config!")
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            ret = cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            ret = cls._instances[cls]
            if hasattr(ret, 'reinit'):
                ret.reinit(*args, **kwargs)

        return ret
