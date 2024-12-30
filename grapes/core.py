"""
Core of the grapes package. Includes the classes for nodes and graphs.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import copy
import inspect

import networkx as nx

starting_node_properties = {
    "type": "standard",
    "has_value": False,
    "value": None,
    "is_frozen": False,
    "is_recipe": False,
    "topological_generation_index": -1,
    "has_reachability": False,
    "reachability": None,
}


class Graph:
    """
    Class that represents a graph of nodes.
    """

    # Class
    def __init__(self, nx_digraph=None):
        # Internally, we handle a nx_digraph
        if nx_digraph == None:
            self._nxdg = nx.DiGraph()
        else:
            self._nxdg = nx_digraph
        # Alias for easy access
        self.nodes = self._nxdg.nodes

    # Class
    def __getitem__(self, node):
        """
        Get the value of a node with []
        """
        return get_value(self, node)

    # Class
    def __setitem__(self, node, value):
        """
        Set the value of a node with []
        """
        set_value(self, node, value)

    # Class
    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return isinstance(other, self.__class__) and nx.is_isomorphic(
            self._nxdg, other._nxdg, dict.__eq__, dict.__eq__
        )


# Get/Set
def get_node_attribute(graph, node, attribute):
    attributes = graph.nodes[node]
    if attribute in attributes and attributes[attribute] is not None:
        return attributes[attribute]
    else:
        raise ValueError("Node " + node + " has no " + attribute)


# Get/Set
def set_node_attribute(graph, node, attribute, value):
    graph.nodes[node][attribute] = value


# Get/Set
def get_value(graph, node):
    if get_node_attribute(graph, node, "value") is not None and get_has_value(
        graph, node
    ):
        return get_node_attribute(graph, node, "value")
    else:
        raise ValueError("Node " + node + " has no value")


# Get/Set
def set_value(graph, node, value):
    # Note: This changes reachability
    set_node_attribute(graph, node, "value", value)
    set_has_value(graph, node, True)


# Get/Set
def unset_value(graph, node):
    # Note: This changes reachability
    set_has_value(graph, node, False)


# Get/Set
def get_has_value(graph, node):
    return get_node_attribute(graph, node, "has_value")


# Get/Set
def set_has_value(graph, node, has_value):
    return set_node_attribute(graph, node, "has_value", has_value)


# Get/Set
def get_type(graph, node):
    return get_node_attribute(graph, node, "type")


# Get/Set
def set_type(graph, node, type):
    return set_node_attribute(graph, node, "type", type)


# Get/Set
def get_is_recipe(graph, node):
    return get_node_attribute(graph, node, "is_recipe")


# Get/Set
def set_is_recipe(graph, node, is_recipe):
    return set_node_attribute(graph, node, "is_recipe", is_recipe)


# Get/Set
def get_recipe(graph, node):
    return get_node_attribute(graph, node, "recipe")


# Get/Set
def set_recipe(graph, node, recipe):
    return set_node_attribute(graph, node, "recipe", recipe)


# Get/Set
def get_args(graph, node):
    return get_node_attribute(graph, node, "args")


# Get/Set
def set_args(graph, node, args):
    return set_node_attribute(graph, node, "args", args)


# Get/Set
def get_kwargs(graph, node):
    return get_node_attribute(graph, node, "kwargs")


# Get/Set
def set_kwargs(graph, node, kwargs):
    return set_node_attribute(graph, node, "kwargs", kwargs)


# Get/Set
def get_conditions(graph, node):
    conditions = get_node_attribute(graph, node, "conditions")
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return conditions


# Get/Set
def set_conditions(graph, node, conditions):
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return set_node_attribute(graph, node, "conditions", conditions)


# Get/Set
def get_possibilities(graph, node):
    possibilities = get_node_attribute(graph, node, "possibilities")
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return possibilities


# Get/Set
def set_possibilities(graph, node, possibilities):
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return set_node_attribute(graph, node, "possibilities", possibilities)


# Get/Set
def get_is_frozen(graph, node):
    return get_node_attribute(graph, node, "is_frozen")


# Get/Set
def set_is_frozen(graph, node, is_frozen):
    return set_node_attribute(graph, node, "is_frozen", is_frozen)


# Get/Set
def get_topological_generation_index(graph, node):
    return get_node_attribute(graph, node, "topological_generation_index")


# Get/Set
def set_topological_generation_index(graph, node, index):
    set_node_attribute(graph, node, "topological_generation_index", index)


# Get/Set
def get_has_reachability(graph, node):
    return get_node_attribute(graph, node, "has_reachability")


# Get/Set
def set_has_reachability(graph, node, has_reachability):
    return set_node_attribute(graph, node, "has_reachability", has_reachability)


# Get/Set
def get_reachability(graph, node):
    if get_node_attribute(
        graph, node, "reachability"
    ) is not None and get_node_attribute(graph, node, "has_reachability"):
        return get_node_attribute(graph, node, "reachability")
    else:
        raise ValueError("Node " + node + " has no reachability")


# Get/Set
def set_reachability(graph, node, reachability):
    if reachability not in ("unreachable", "uncertain", "reachable"):
        raise ValueError(reachability + " is not a valid reachability value.")
    set_node_attribute(graph, node, "reachability", reachability)
    set_node_attribute(graph, node, "has_reachability", True)


# Get/Set
def unset_reachability(graph, node):
    set_node_attribute(graph, node, "has_reachability", False)
