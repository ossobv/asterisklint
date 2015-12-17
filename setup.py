import os
from distutils.core import setup


def get_packages():
    here = os.path.dirname(__file__)
    superdir = os.path.join(here, 'asterisklint')
    packages = []
    for root, dirs, files in os.walk(superdir):
        packages.append(root.replace('/', '.'))
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
    packages.sort()
    return packages


if __name__ == '__main__':
    long_descriptions = []
    with open('README.rst') as file:
        long_descriptions.append(file.read())
    with open('CHANGES.rst') as file:
        long_descriptions.append(file.read())
    with open('CHANGES.rst') as file:
        version = file.read(31).strip().split(' ')[0]

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
            'Topic :: Communications :: Telephony',
            'Topic :: Software Development :: Pre-processors',
        ],
    )

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
