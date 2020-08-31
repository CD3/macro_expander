#! /usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    # long_description = f.read()
long_description= ""

setup(
    name='macro_expander',
    license="MIT",
    version = '0.3',
    description='Expand macros within a text string. Somewhere between formatting and templating.',
    url='https://github.com/CD3/macro_expander',
    author='C.D. Clark III',
    packages=find_packages(),
    install_requires=['pyparsing'],
    entry_points='''
    [console_scripts]
    expand-macros.py=macro_expander.scripts.expand_macros:main
    ''',
)
