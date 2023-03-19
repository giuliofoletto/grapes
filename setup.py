"""
Setup file to install grapes as a package.

Usage: pip install .

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from setuptools import setup

# Assign the content of README.md to long_description
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='grapes',
      version='0.7.0',
      description='Helper for dataflow based programming',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/giuliofoletto/grapes',
      author='Giulio Foletto',
      author_email='giulio.foletto@outlook.com',
      license='Apache',
      license_files=('LICENSE.txt', 'NOTICE.txt'),
      packages=['grapes'],
      install_requires=[
          'networkx',
          "tomli;python_version<'3.11'"
      ],
      extras_require={
          'visualize': ['pygraphviz', 'matplotlib'],  # For installation of pygraphviz, refer to https://pygraphviz.github.io/documentation/stable/install.html
          'testing': ['pytest']
      },
      zip_safe=False)
