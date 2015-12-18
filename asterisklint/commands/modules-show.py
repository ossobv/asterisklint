"""
Show which modules, apps and functions are used by the dialplan. Takes
'extensions.conf' as argument.
"""
import argparse
from collections import defaultdict

from asterisklint import FileDialplanParser
from asterisklint.application import AppLoader
from asterisklint.defines import MessageDefManager
from asterisklint.varfun import FuncLoader


def main(args, envs):
    parser = argparse.ArgumentParser(
        description=(
            "Show which modules, apps and functions are used by the dialplan. "
            "Useful when you use autoload=no in your modules.conf. Beware "
            "that you do need more modules than just these listed."))
    parser.add_argument(
        'dialplan', metavar='EXTENSIONS_CONF',
        help="path to extensions.conf")
    args = parser.parse_args(args)

    MessageDefManager.muted = True  # no messages to stderr

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
