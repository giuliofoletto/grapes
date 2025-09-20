"""
Easy example of usage of grapes to compute properties of an ideal gas.
Described in detail in USAGE.md.
"""

import grapes as gr


# Functions for the steps
def calculate_T(P, V, n, R):
    return P * V / (n * R)


def calculate_U(n, R, T):
    return 3 / 2 * n * R * T


# Definition of the graph
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

# First example of execution
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

# Define the new context
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

# Re-execute with the original context
result = gr.execute_graph_from_context(g, context, target)
print(result["U"], "J")  # 15198.75 J

# Execute with a different target
target = "T"
result = gr.execute_graph_from_context(g, context, target)
print(result["T"], "K")  # 1218.73 K

# Visualize the graph
# Utility code to get folder name
import os

visualizations_folder_name = (
    os.path.dirname(os.path.realpath(__file__)) + "/visualizations/"
)
gv = gr.get_graphviz_digraph(
    g,
    hide_recipes=True,
    rankdir="TB",
    splines="ortho",
)
gr.write_dotfile(gv, visualizations_folder_name + "ideal_gas.gv")
gr.draw_to_file(
    gv, visualizations_folder_name + "ideal_gas.pdf", format="pdf", prog="dot"
)
print("Graph saved to", visualizations_folder_name + "ideal_gas.pdf")
