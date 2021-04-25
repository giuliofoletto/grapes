# QFlow

A simple library for dataflow programming in python. Inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.
The name QFlow is not definitive.

## Dependencies
QFlow depends only on [`networkx`](https://github.com/networkx/networkx), which is included in Anaconda.
To visualize graphs, [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) is also needed.
For its installation, refer to the official [guide](https://pygraphviz.github.io/documentation/stable/install.html).
Finally, [`pytest`](https://github.com/pytest-dev/pytest) is needed to run the tests.

## Installation
Move to the root directory of the QFlow source code (the one where `setup.py` is located) and run
```console
pip install -e .
```

## Copyright
The bulk of QFlow development was done by Giulio Foletto in his spare time. The plan is to release this code in an open manner. However, for the moment Giulio Foletto retains all copyright.