from setuptools import setup

setup(name='qflow',
      version='0.1',
      description='Helper for dataflow based programming',
      author='Giulio Foletto',
      author_email='giulio.foletto@outlook.com',
      license='MIT',
      packages=['qflow'],
      install_requires=[
          'graphviz'
      ],
      zip_safe=False)