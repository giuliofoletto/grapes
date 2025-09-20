# Usage and examples

`grapes` allows you to organize your computation as a directed acyclic graph (DAG).
This is useful when you have a complex computation with many intermediate steps, and you want to be able to easily change the inputs and outputs.
You can define very complex graphs with many nodes, and then select at runtime which nodes to use as inputs and which nodes to compute as outputs.
`grapes` handles the dependency resolution and the execution of the graph for you, avoiding redundant or unnecessary calculations.
It also allows you to easily visualize the calculation as a graph.

## Ideal gas example

Here is a simple example of how to use `grapes` to compute the internal energy $U$ of an ideal gas given its pressure $P$, volume $V$, its number of moles $n$, and the universal constant of ideal gases $R$.

You can first think about how you would solve the problem on paper, and realize that
$$ T = \frac{PV}{nR} $$
and that
$$ U = \frac32 nRT $$

Then you can translate this to pure python functions:

```python
def calculate_T(P, V, n, R):
    return P*V/(n*R)

def calculate_U(n, R, T):
    return 3/2*n*R*T
```

Rather than defining a procedure (or a larger function) that takes `P`, `V`, `n`, and `R` as inputs and returns `U` as output, you can define a graph with two steps, one for each of the two functions above.

```python
# Create the graph object
g = gr.Graph()

# Add the two steps
gr.add_step(g, "T", "calculate_T", "P", "V", "n", "R")
gr.add_step(g, "U", "calculate_U", "n", "R", "T")

# Bind the two functions to the two steps
gr.update_internal_context(
    g,
    {
        "calculate_T": calculate_T,  # defined earlier
        "calculate_U": calculate_U,
    },
)

# End the definition of the graph
gr.finalize_definition(g)
```

Now you can execute the graph by providing the input values of `P`, `V`, `n`, and `R`, and specifying that you want to compute `U`.
Note that in `grapes`, the input is called context, and the output is called target.

```python
# Define the context
context = {
    "P": 101325,  # Pa
    "V": 0.1,  # m^3
    "n": 1,  # mol
    "R": 8.314,  # J/(mol K)
}
# Define the target
target = "U"
# Execute the graph
result = gr.execute_graph_from_context(g, context, target)
# result is now another graph with the value of U
print(result["U"], "J")  # 15198.75 J
```

Now imagine that you are not given `n`, but rather the mass `m` of the gas (in kg) and its molar mass `M` (in g/mol).
You can add another step to the graph to compute `n` from `m` and `M` using the equation
$$ n = 10^3\cdot\frac{m}{M} $$

```python
# Change the graph to compute n from m and M
gr.add_step(g, "n", "calculate_n", "m", "M")
gr.update_internal_context(
    g,
    {
        "calculate_n": lambda m, M: 1e3
        * m
        / M,  # alternative definition via lambda, rather than a named function
    },
)
gr.finalize_definition(g)
```

You can now execute the graph again, this time providing `m` and `M` instead of `n`.

```python
new_context = {
    "P": 101325,  # Pa
    "V": 0.1,  # m^3
    "m": 0.032,  # kg (mass of O2)
    "M": 32,  # g/mol (molar mass of O2)
    "R": 8.314,  # J/(mol K)
}
# Execute the graph
result = gr.execute_graph_from_context(g, new_context, target)
print(result["U"], "J")  # 15198.75 J
```

Note that the execution code has not changed.
We have simply provided a different context, and the graph has automatically figured out that it needs to calculate $n$ first.
Most importantly, although the graph has changed, the original execution code still works as before, and produces the same result.

```python
# Re-execute with the original context
result = gr.execute_graph_from_context(g, context, target)
print(result["U"], "J")  # 15198.75 J
```

So even if you add complexity to the graph, you can still use it for simple executions, without changing the code.

Of course, you can also change the target to compute something else, for example the temperature `T`:

```python
target = "T"
result = gr.execute_graph_from_context(g, context, target)
print(result["T"], "K")  # 1218.73 K
```

The full code of this example is available in the [`examples/gas/main.py`](examples/gas/main.py) file.

## Visualization

You can visualize the graph using Graphviz.

```python
gv = gr.get_graphviz_digraph(
    g,
    hide_recipes=True,
    pretty_names=True,
    color_mode="by_generation",
    rankdir="TB",
    splines="ortho",
)
gr.draw_to_screen(gv, format="png", prog="dot")
```

You can also write to a dotfile or save the rendered graph to a file.

```python
gr.write_dotfile(gv, "ideal_gas.gv")
gr.draw_to_file(gv, "ideal_gas.pdf", format="pdf", prog="dot")
print("Graph saved to ideal_gas.pdf")
```
