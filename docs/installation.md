# Installation

`grapes` is available on [PyPI](https://pypi.org/project/grapes/).
Install it from there with

```console
pip install grapes
```

This takes care of installing the dependencies as well (listed in [pyproject.toml](pyproject.toml)).

Caveat: when pip tries to install the dependency [`pygraphviz`](https://github.com/pygraphviz/pygraphviz), it might fail if you don't have its binary dependencies installed.
A simple way tho solve this is to first install `pygraphviz` from [conda-forge](https://conda-forge.org/) and then proceed with the installation of `grapes`.
