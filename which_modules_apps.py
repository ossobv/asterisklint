#!/usr/bin/env python3
"""
Show which modules and apps are used by the dialplan.
"""
from collections import defaultdict
import sys

from asterisklint import FileDialplanParser
from asterisklint.application import AppLoader


loader = AppLoader()
parser = FileDialplanParser()
parser.include(sys.argv[1])
dialplan = next(iter(parser))

used_apps_per_module = defaultdict(list)
for app in loader.used_apps:
    used_apps_per_module[app.module].append(app)

print('Application providing modules used:')
for module in loader.used_modules:
    apps = used_apps_per_module[module][:]
    app_lines = ['']
    while apps:
        next_ = apps.pop(0)
        if app_lines[-1]:
            app_lines[-1] += ', '
        formatted = '{}()'.format(next_.name)
        if len(app_lines[-1]) + len(formatted) > 52:
            app_lines.append(formatted)
        else:
            app_lines[-1] += formatted

    # Output.
    print('  {:20s}  {}'.format(
        module, app_lines[0]))
    for app_line in app_lines[1:]:
        print('  {:20s}  {}'.format(
            '', app_line))
