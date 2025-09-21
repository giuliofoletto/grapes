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
        """
        Initialize a Graph object.

        Parameters
        ----------
        nx_digraph : networkx.DiGraph, optional
            A pre-existing directed graph to initialize from. If None, an empty graph is created. Default is None.
        """
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

        Parameters
        ----------
        node : hashable (typically string)
            Name of the node whose value is to be retrieved

        Returns
        -------
        value : any
            Value of the node

        Raises
        ------
        ValueError
            If the node has no value
        KeyError
            If the node does not exist
        """
        return get_value(self, node)

    def __setitem__(self, node, value):
        """
        Set the value of a node with []

        Parameters
        ----------
        node : hashable (typically string)
            Name of the node whose value is to be set
        value : any
            Value to set

        Raises
        ------
        KeyError
            If the node does not exist
        """
        set_value(self, node, value)

    def __eq__(self, other):
        """
        Equality check based on all members.

        Parameters
        ----------
        other : Graph
            Graph to compare with

        Returns
        -------
        bool
            True if the graphs are equal, False otherwise

        Notes
        -----
        Two graphs are equal if they are isomorphic and all their node and edge attributes are equal (including values).
        """
        return isinstance(other, self.__class__) and nx.is_isomorphic(
            self._nxdg, other._nxdg, dict.__eq__, dict.__eq__
        )
