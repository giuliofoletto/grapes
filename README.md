# grapes 

A simple library for dataflow programming in python.
It is inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.

## Dependencies
`grapes` depends only on [`networkx`](https://github.com/networkx/networkx), which can be found on PyPI and is included in the Anaconda distribution.
To visualize graphs, [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) is also needed.
For its installation, refer to the official [guide](https://pygraphviz.github.io/documentation/stable/install.html).
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

## Roadmap
Future plans include:

* Better explanation of what `grapes` is.
* Usage examples.
* Better comments and documentation.

## Authorship and License
The bulk of `grapes` development was done by Giulio Foletto in his spare time.
See `LICENSE.txt` and `NOTICE.txt` for details on how `grapes` is distributed.