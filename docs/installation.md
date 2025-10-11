# Installation

`grapes` is available on [conda-forge](https://anaconda.org/conda-forge/grapes) and on [PyPI](https://pypi.org/project/grapes/).
Install it with

```console
conda install conda-forge::grapes
```

or

```console
pip install grapes
```

This takes care of installing the dependencies as well (listed in `pyproject.toml` in the root directory).

Caveat: the automatic installation of the binary dependency [`graphviz`](https://graphviz.org) happens only if you use conda.
If you want to use pip, you must install it [manually](https://graphviz.org/download/).
