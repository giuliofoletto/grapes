# grapes

A simple library for dataflow programming in python.
It allows you to organize your computation as a directed acyclic graph.

## Quickstart

For more complete documentation, please refer to the files in the `docs/` folder.
Here's what you need to know to get started quickly.

Install `grapes` from PyPI with

```console
pip install grapes
```

Define a graph by adding steps and binding functions to them:

```python
import grapes as gr
g = gr.Graph()
gr.add_step(g, "b", "compute_b", "a")
gr.add_step(g, "c", "compute_c", "b")
gr.update_internal_context(g,
    {
        "compute_b": lambda a: 2*a,
        "compute_c": lambda b: b+1
    }
)
gr.finalize_definition(g)
```

Execute the graph to find your target, starting from your input context.

```python
context = {"a": 3}
target = "c"
result = gr.execute_graph_from_context(g, context, target)
print(result["c"])  # 7
```

## Additional remarks

The bulk of `grapes` development was done by Giulio Foletto in his spare time.
See `LICENSE.txt` and `NOTICE.txt` for details on how `grapes` is distributed.

`grapes` is inspired by [`pythonflow`](https://github.com/spotify/pythonflow) but with substantial modifications.

It relies internally on [`networkx`](https://networkx.org/) for graph management and on [`pygraphviz`](https://github.com/pygraphviz/pygraphviz) for graph visualization.

Most of the development of `grapes` was done before AI coding tools were available.
However, recent edits (September 2025) were assisted by GitHub Copilot, especially for writing docstrings.
