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
        return self.get_value(node)

    # Class
    def __setitem__(self, node, value):
        """
        Set the value of a node with []
        """
        self.set_value(node, value)

    # Class
    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return isinstance(other, self.__class__) and nx.is_isomorphic(
            self._nxdg, other._nxdg, dict.__eq__, dict.__eq__
        )

    # Get/Set
    def get_node_attribute(self, node, attribute):
        attributes = self.nodes[node]
        if attribute in attributes and attributes[attribute] is not None:
            return attributes[attribute]
        else:
            raise ValueError("Node " + node + " has no " + attribute)

    # Get/Set
    def set_node_attribute(self, node, attribute, value):
        self.nodes[node][attribute] = value

    # Get/Set
    def get_value(self, node):
        if self.get_node_attribute(node, "value") is not None and self.get_has_value(
            node
        ):
            return self.get_node_attribute(node, "value")
        else:
            raise ValueError("Node " + node + " has no value")

    # Get/Set
    def set_value(self, node, value):
        # Note: This changes reachability
        self.set_node_attribute(node, "value", value)
        self.set_has_value(node, True)

    # Get/Set
    def unset_value(self, node):
        # Note: This changes reachability
        self.set_has_value(node, False)

    # Get/Set
    def get_reachability(self, node):
        if self.get_node_attribute(
            node, "reachability"
        ) is not None and self.get_node_attribute(node, "has_reachability"):
            return self.get_node_attribute(node, "reachability")
        else:
            raise ValueError("Node " + node + " has no reachability")

    # Get/Set
    def set_reachability(self, node, reachability):
        if reachability not in ("unreachable", "uncertain", "reachable"):
            raise ValueError(reachability + " is not a valid reachability value.")
        self.set_node_attribute(node, "reachability", reachability)
        self.set_node_attribute(node, "has_reachability", True)

    # Get/Set
    def unset_reachability(self, node):
        self.set_node_attribute(node, "has_reachability", False)

    # Get/Set
    def get_is_recipe(self, node):
        return self.get_node_attribute(node, "is_recipe")

    # Get/Set
    def set_is_recipe(self, node, is_recipe):
        return self.set_node_attribute(node, "is_recipe", is_recipe)

    # Get/Set
    def get_recipe(self, node):
        return self.get_node_attribute(node, "recipe")

    # Get/Set
    def set_recipe(self, node, recipe):
        return self.set_node_attribute(node, "recipe", recipe)

    # Get/Set
    def get_args(self, node):
        return self.get_node_attribute(node, "args")

    # Get/Set
    def set_args(self, node, args):
        return self.set_node_attribute(node, "args", args)

    # Get/Set
    def get_kwargs(self, node):
        return self.get_node_attribute(node, "kwargs")

    # Get/Set
    def set_kwargs(self, node, kwargs):
        return self.set_node_attribute(node, "kwargs", kwargs)

    # Get/Set
    def get_conditions(self, node):
        conditions = self.get_node_attribute(node, "conditions")
        if not isinstance(conditions, list):
            conditions = list(conditions)
        return conditions

    # Get/Set
    def set_conditions(self, node, conditions):
        if not isinstance(conditions, list):
            conditions = list(conditions)
        return self.set_node_attribute(node, "conditions", conditions)

    # Get/Set
    def get_possibilities(self, node):
        possibilities = self.get_node_attribute(node, "possibilities")
        if not isinstance(possibilities, list):
            possibilities = list(possibilities)
        return possibilities

    # Get/Set
    def set_possibilities(self, node, possibilities):
        if not isinstance(possibilities, list):
            possibilities = list(possibilities)
        return self.set_node_attribute(node, "possibilities", possibilities)

    # Get/Set
    def get_type(self, node):
        return self.get_node_attribute(node, "type")

    # Get/Set
    def set_type(self, node, type):
        return self.set_node_attribute(node, "type", type)

    # Get/Set
    def get_topological_generation_index(self, node):
        return self.get_node_attribute(node, "topological_generation_index")

    # Get/Set
    def set_topological_generation_index(self, node, index):
        self.set_node_attribute(node, "topological_generation_index", index)

    # Get/Set
    def get_is_frozen(self, node):
        return self.get_node_attribute(node, "is_frozen")

    # Get/Set
    def set_is_frozen(self, node, is_frozen):
        return self.set_node_attribute(node, "is_frozen", is_frozen)

    # Get/Set
    def get_has_value(self, node):
        return self.get_node_attribute(node, "has_value")

    # Get/Set
    def set_has_value(self, node, has_value):
        return self.set_node_attribute(node, "has_value", has_value)

    # Get/Set
    def get_has_reachability(self, node):
        return self.get_node_attribute(node, "has_reachability")

    # Get/Set
    def set_has_reachability(self, node, has_reachability):
        return self.set_node_attribute(node, "has_reachability", has_reachability)
