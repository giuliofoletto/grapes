from setuptools import setup

setup(name='qflow',
      version='0.3',
      description='Helper for dataflow based programming',
      author='Giulio Foletto',
      author_email='giulio.foletto@outlook.com',
      license='MIT',
      packages=['qflow'],
      install_requires=[
          'networkx',
      ],
      extras_require={
          'visualize': ['pygraphviz'],  # Refer to https://pygraphviz.github.io/documentation/stable/install.html
          'testing': ['pytest']
      },
      zip_safe=False)
