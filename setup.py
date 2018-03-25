#! /usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path
import version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    # long_description = f.read()
long_description= ""

print("version:",version.__version__)
setup(
    name='macro_expander',
    version=version.__version__,
    description='Expand macros within a text string. Somewhere between formatting and templating.',
    long_description=long_description,  # Optional
    url='https://github.com/CD3/macro_expander',
    author='C.D. Clark III',
    packages=["macro_expander"],
)
