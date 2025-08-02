"""
Core of the grapes package. Includes the Graph class.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import networkx as nx

from .features import get_value, set_value


class Graph:
    """
    Class that represents a graph of nodes.
    """

    def __init__(self, nx_digraph=None):
        # Internally, we handle a nx_digraph
        if nx_digraph == None:
            self._nxdg = nx.DiGraph()
        else:
            self._nxdg = nx_digraph
        # Alias for easy access
        self.nodes = self._nxdg.nodes

    def __getitem__(self, node):
        """
        Get the value of a node with []
        """
        return get_value(self, node)

    def __setitem__(self, node, value):
        """
        Set the value of a node with []
        """
        set_value(self, node, value)

    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return isinstance(other, self.__class__) and nx.is_isomorphic(
            self._nxdg, other._nxdg, dict.__eq__, dict.__eq__
        )
