# grapes

A simple library for dataflow programming in python.
It allows you to organize your computation as a directed acyclic graph.

## Installation

`grapes` is available on [PyPI](https://pypi.org/project/grapes/).
Install it from there with

```console
pip install grapes
```

This takes care of installing the dependencies as well (listed in [pyproject.toml](pyproject.toml)).

Caveat: when pip tries to install the dependency [`pygraphviz`](https://github.com/pygraphviz/pygraphviz), it might fail if you don't have its binary dependencies installed.
A simple way tho solve this is to first install `pygraphviz` from [conda-forge](https://conda-forge.org/) and then proceed with the installation of `grapes`.

## Usage

See [`USAGE.md`](USAGE.md) for a detailed explanation of how to use `grapes`, with examples.

## Acknowledgements

`grapes` is inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.

It relies internally on [`networkx`](https://networkx.org/) for graph management and on [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) for graph visualization.

## Authorship and License

The bulk of `grapes` development was done by Giulio Foletto in his spare time.
See `LICENSE.txt` and `NOTICE.txt` for details on how `grapes` is distributed.
