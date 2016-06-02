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
"""
Show which modules, apps and functions are used by the dialplan. Takes
'extensions.conf' as argument.
"""
import argparse
from collections import defaultdict

from asterisklint import FileDialplanParser
from asterisklint.application import E_APP_MISSING, AppLoader
from asterisklint.defines import MessageDefManager
from asterisklint.mainutil import UniqueStore, load_func_odbc_functions
from asterisklint.varfun import E_FUNC_MISSING, FuncLoader


class Aggregator(object):
    """
    Collector of all E_APP_MISSING, E_FUNC_MISSING errors. We want to
    know about these things.
    """
    def __init__(self):
        E_APP_MISSING.add_callback(self.on_e_app_missing)
        E_FUNC_MISSING.add_callback(self.on_e_func_missing)
        self.unknown_apps = set()
        self.unknown_funcs = set()

    def on_e_app_missing(self, message):
        self.unknown_apps.add(message.fmtkwargs['app'])

    def on_e_func_missing(self, message):
        self.unknown_funcs.add(message.fmtkwargs['func'])


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            "Show which modules, apps and functions are used by the dialplan. "
            "Useful when you use autoload=no in your modules.conf. Beware "
            "that you do need more modules than just these listed."))
    parser.add_argument(
        'dialplan', metavar='EXTENSIONS_CONF', nargs='?',
        default='./extensions.conf',
        help='path to extensions.conf')
    parser.add_argument(
        '--func-odbc', metavar='FUNC_ODBC_CONF', action=UniqueStore,
        help="path to func_odbc.conf, will be read automatically if found "
             "in same the same dir as extensions.conf; set empty to disable")
    args = parser.parse_args(args)

    # No messages to stderr, but do collect the E_APP_MISSING and
    # E_FUNC_MISSING errors.
    aggregator = Aggregator()
    MessageDefManager.muted = True

    # Load func_odbc functions if requested.
    load_func_odbc_functions(args.func_odbc, args.dialplan)

    parser = FileDialplanParser()
    parser.include(args.dialplan)
    dialplan = next(iter(parser))
    del dialplan

    apploader = AppLoader()
    funcloader = FuncLoader()
    all_modules = set()

    for what, used_items, used_modules in (
            ('Application', apploader.used_apps, apploader.used_modules),
            ('Function', funcloader.used_funcs, funcloader.used_modules)):
        all_modules.update(used_modules)

        used_items_per_module = defaultdict(list)
        for item in used_items:
            used_items_per_module[item.module].append(item)

        print('; {} providing modules used:'.format(what))
        for module in used_modules:
            items = used_items_per_module[module][:]
            item_lines = ['']
            while items:
                next_ = items.pop(0)
                if item_lines[-1]:
                    item_lines[-1] += ', '
                formatted = '{}()'.format(next_.name)
                if len(item_lines[-1]) + len(formatted) > 52:
                    item_lines.append(formatted)
                else:
                    item_lines[-1] += formatted

            # Output.
            print(';   {:20s}  {}'.format(
                module, item_lines[0].strip()))
            for item_line in item_lines[1:]:
                print(';   {:20s}  {}'.format(
                    '', item_line.strip()))
        print(';')

    print('; modules.conf')
    for module in sorted(all_modules):
        if module != '<builtin>':
            print('load => {}.so'.format(module))
    print()
    if aggregator.unknown_apps:
        print('; WARNING: The following unknown applications were seen:')
        print(';   {}'.format(', '.join(sorted(aggregator.unknown_apps))))
        print(';')
    if aggregator.unknown_funcs:
        print('; WARNING: The following unknown functions were seen:')
        print(';   {}'.format(', '.join(sorted(aggregator.unknown_funcs))))
        print(';')

    return int(bool(aggregator.unknown_apps) or bool(aggregator.unknown_funcs))
