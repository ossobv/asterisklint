#!/usr/bin/env python3
"""
Show which modules and apps are used by the dialplan.
"""
from collections import defaultdict
import sys

from asterisklint import FileDialplanParser
from asterisklint.application import AppLoader
from asterisklint.varfun import FuncLoader


parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))

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

    print('{} providing modules used:'.format(what))
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
        print('  {:20s}  {}'.format(
            module, item_lines[0]))
        for item_line in item_lines[1:]:
            print('  {:20s}  {}'.format(
                '', item_line))
    print()

print('; modules.conf')
for module in sorted(all_modules):
    print('load => {}.so'.format(module))
print()
