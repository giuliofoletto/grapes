# QFlow

A simple library for dataflow programming in python. Inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.
The name QFlow is not definitive.

## Dependencies
QFlow itself has no dependencies (except python itself), however, if you want to visualize graphs, you need to install [Graphviz](https://graphviz.org/) and its python wrapper.
It is advised to do this with `conda`:
```console
conda install -y graphviz python-graphviz
```

If you need to run test, also install `pytest`:
```console
pip install pytest
```

## Installation
Move to the root directory of the QFlow source code (the one where `setup.py` is located) and run
```console
pip install -e .
```

## Copyright
The bulk of QFlow development was done by Giulio Foletto in his spare time. The plan is to release this code in an open manner. However, for the moment Giulio Foletto retains all copyright.