# grapes 

It is a simple library for dataflow programming in python.
It is inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.

## Dependencies
grapes depends only on [`networkx`](https://github.com/networkx/networkx), which is included in Anaconda.
To visualize graphs, [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) is also needed.
For its installation, refer to the official [guide](https://pygraphviz.github.io/documentation/stable/install.html).
Finally, [`pytest`](https://github.com/pytest-dev/pytest) is needed to run the tests.

## Installation
Move to the root directory of the grapes source code (the one where `setup.py` is located) and run
```console
pip install -e .
```

## Roadmap
Future plans include:

* Better explanation of what `grapes` is.
* Usage examples.
* Better comments and documentation.

## Authorship and License
The bulk of `grapes` development was done by Giulio Foletto in his spare time.
See the project-level license file for details on how `grapes` is distributed.