# Installation

`grapes` is available on [PyPI](https://pypi.org/project/grapes/).
Install it from there with

```console
pip install grapes
```

This takes care of installing the dependencies as well (listed in `pyproject.toml` in the root directory).

Caveat: when pip installs the dependency [`pygraphviz`](https://github.com/pygraphviz/pygraphviz), it does not install its binary dependency [`graphviz`](https://graphviz.org).
You can either install it [manually](https://graphviz.org/download/) or install `pygraphviz` from [conda-forge](https://conda-forge.org/) instead of pip.
