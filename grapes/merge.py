"""
Functions to merge, split and verify the compatibility of graphs.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import copy
import inspect

import networkx as nx

from .core import Graph
from .features import get_has_value, get_type, get_value


def check_compatibility_nodes(first_graph, first_node, second_graph, second_node):
    # If types differ, return False
    if get_type(first_graph, first_node) != get_type(second_graph, second_node):
        return False
    # If nodes are equal, return True
    if first_graph.nodes[first_node] == second_graph._nxdg.nodes[second_node]:
        return True
    # If they both have values but they differ, return False. If only one has a value, proceed
    if (
        get_has_value(first_graph, first_node)
        and get_has_value(second_graph, second_node)
        and get_value(first_graph, first_node) != get_value(second_graph, second_node)
    ):
        # Plot twist! Both are functions and have the same code: proceed
        if (
            inspect.isfunction(get_value(first_graph, first_node))
            and inspect.isfunction(get_value(second_graph, second_node))
            and get_value(first_graph, first_node).__code__.co_code
            == get_value(second_graph, second_node).__code__.co_code
        ):
            pass
        else:
            return False
    # If they both have dependencies but they differ, return False. If only one has dependencies, proceed
    predecessors = list(first_graph._nxdg.predecessors(first_node))
    other_predecessors = list(second_graph._nxdg.predecessors(second_node))
    if (
        len(predecessors) != 0
        and len(other_predecessors) != 0
        and predecessors != other_predecessors
    ):
        return False
    # Return True if at least one has no dependencies (or they are the same), at least one has no value (or they are the same)
    return True


def check_compatibility(first, second):
    """
    Check if two graphs can be composed. Currently DAG status is not verified.
    """
    if not isinstance(first, Graph) or not isinstance(second, Graph):
        return False
    common_nodes = first.nodes & second._nxdg.nodes  # Intersection
    for key in common_nodes:
        if not check_compatibility_nodes(first, key, second, key):
            return False
    return True


def merge_two(first, second):
    """
    Merge two graphs.
    """
    if not check_compatibility(first, second):
        raise ValueError("Cannot merge incompatible graphs")
    res = nx.compose(first._nxdg, second._nxdg)
    # If a node in first has value, but its counterpart in second has not, the value must be recovered
    for key in nx.intersection(first._nxdg, second._nxdg):
        if (
            not second._nxdg.nodes[key]["has_value"]
            and first._nxdg.nodes[key]["has_value"]
        ):
            res.nodes[key]["has_value"] = True
            res.nodes[key]["value"] = first._nxdg.nodes[key]["value"]
    return Graph(nx_digraph=res)


def merge(*graphs):
    """
    Merge any number (>=2) of graphs.
    """
    if len(graphs) < 2:
        raise ValueError("At least two graphs are required to merge")
    elif len(graphs) == 2:
        return merge_two(graphs[0], graphs[1])
    else:
        return merge(merge_two(graphs[0], graphs[1]), *graphs[2:])


def get_subgraph(graph, nodes):
    res = copy.deepcopy(graph)
    res._nxdg.remove_nodes_from([n for n in graph._nxdg if n not in nodes])
    return res
