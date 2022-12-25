# grapes 

A simple library for dataflow programming in python.
It is inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.

## Dependencies
The core `grapes` module depends only on [`networkx`](https://github.com/networkx/networkx), which can be found on PyPI and is included in the Anaconda distribution.

To visualize graphs, [`matplotlib`](https://matplotlib.org/) and [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) (a wrapper for [`Graphviz`](https://graphviz.org/)) are also needed.
On  Windows, `pygraphviz` requires the [Visual Studio C/C++ build tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) to be installed (including MSVC tools), alongside [`Graphviz` 2.46](https://gitlab.com/graphviz/graphviz/-/package_files/6164164/download) or higher, which should be in `PATH`.
This is explained in detail in the official [guide](https://pygraphviz.github.io/documentation/stable/install.html) of `pygraphviz`.

Finally, [`pytest`](https://github.com/pytest-dev/pytest) is needed to run the tests.

## Installation
`grapes` is available on [PyPI](https://pypi.org/project/grapes/).
Install it from there with
```console
pip install grapes
```

Otherwise you can install from source.
Move to the root directory of the grapes source code (the one where `setup.py` is located) and run
```console
pip install -e .
```
The `-e` flag creates an editable installation.

Note that the dependencies related to graph visualization are not installed automatically and should be installed manually as explained in the [Dependencies](#dependencies) section.

## Roadmap
Future plans include:

* Better explanation of what `grapes` is.
* Usage examples.
* Better comments and documentation.

## Authorship and License
The bulk of `grapes` development was done by Giulio Foletto in his spare time.
See `LICENSE.txt` and `NOTICE.txt` for details on how `grapes` is distributed.