import sys
from distutils.core import setup
from os import walk
from os.path import abspath, dirname, join


def get_packages():
    here = dirname(abspath(__file__))
    superdir = join(here, 'asterisklint')
    packages = []
    for root, dirs, files in walk(superdir):
        packages.append(root[len(here) + 1:].replace('/', '.'))
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
    packages.sort()
    return packages


if __name__ == '__main__':
    if sys.version_info < (3,):
        raise NotImplementedError(
            "I'm sorry, but asterisklint works with Python3+ only")

    long_descriptions = []
    with open(join(dirname(__file__), 'README.rst')) as file:
        long_descriptions.append(file.read())
    with open(join(dirname(__file__), 'CHANGES.rst')) as file:
        long_descriptions.append(file.read())
    version = long_descriptions[-1].strip().split(' ', 1)[0]

    setup(
        name='asterisklint',
        version=version,
        scripts=['scripts/asterisklint'],
        packages=get_packages(),
        data_files=[('', ['CHANGES.rst', 'LICENSE', 'README.rst'])],
        description='Asterisk PBX configuration syntax checker',
        long_description=('\n\n\n'.join(long_descriptions)),
        author='Walter Doekes, OSSO B.V.',
        author_email='wjdoekes+asterisklint@osso.nl',
        url='https://github.com/ossobv/asterisklint',
        license='GPLv3+',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            ('License :: OSI Approved :: GNU General Public License v3 '
             'or later (GPLv3+)'),
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Communications :: Telephony',
            'Topic :: Software Development :: Pre-processors',
        ],
    )

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
