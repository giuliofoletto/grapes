"""
Tools that allow the visualization of a graph using graphviz. Requires pygraphviz.

Author: Giulio Foletto.
"""

# import graphviz
import networkx
from .. import *


def get_graphviz_digraph(graph, hide_recipes=False, pretty_names=False, include_values=False, **attrs):
    # Get a graphviz AGraph
    g = nx.drawing.nx_agraph.to_agraph(graph._nxdg)
    # Add attributes to the AGraph
    g.graph_attr.update(**attrs)

    for node_name in g.nodes():
        new_attrs = {}
        node = graph._nxdg.nodes[node_name]

        # Remove recipes if needed, or eliminate attribute of function
        if node["is_recipe"] and hide_recipes:
            g.remove_node(node_name)
            continue
        elif node["is_recipe"] and node["has_value"]:
            new_attrs.update(value="function")

        # Prettify label if required
        label = prettify_label(node_name) if pretty_names else node_name

        # Add values to the label if required
        if include_values and node.attr["has_value"]:
            if isinstance(node.attr["value"], float):
                value_in_label = "{:.2e}".format(node.attr["value"])
            else:
                value_in_label = str(node.attr["value"])
            label += "\n" + value_in_label.partition('\n')[0]
            if value_in_label.find("\n") != -1:
                label += "\n..."

        # Manipulate shapes
        if node["is_recipe"]:
            shape = "ellipse"
        elif node["type"] == "conditional":
            shape = "diamond"
        else:
            shape = "box"

        # Pass these attirbutes to the actual AGraph
        new_attrs.update(label=label, shape=shape)
        g.get_node(node_name).attr.update(new_attrs)

        # Handle edge shapes
        special_dependencies = []
        if node["type"] == "standard" and "recipe" in node:
            if not hide_recipes:
                g.get_edge(node["recipe"], node_name).attr.update(arrowhead="dot")
            special_dependencies.append(node["recipe"])
        elif node["type"] == "conditional":
            for condition in node["conditions"]:
                g.get_edge(condition, node_name).attr.update(arrowhead="diamond")
            special_dependencies.extend(node["conditions"])

    # Return the AGraph (no layout is computed yet)
    return g


def prettify_label(name):
    return "".join(c.upper() if ((i > 0 and name[i-1] == "_") or i == 0) else c for i, c in enumerate(name)).replace("_", " ")
