from setuptools import setup

setup(name='qflow',
      version='0.2',
      description='Helper for dataflow based programming',
      author='Giulio Foletto',
      author_email='giulio.foletto@outlook.com',
      license='MIT',
      packages=['qflow'],
      extras_require={
          'visualize': ['graphviz'],  # If conda is used, it's better to run conda install -y graphviz python-graphviz rather than this
          'testing': ['pytest']
      },
      zip_safe=False)
