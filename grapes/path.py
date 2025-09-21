"""
Functions to get the path needed to reach a target from valued nodes

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .features import (
    get_conditions,
    get_has_value,
    get_possibilities,
    get_type,
    get_value,
)


def get_path_to_target(graph, target):
    """
    Get the path from the last valued nodes to a target node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    target : str
        The name of the target node.

    Returns
    -------
    set
        Set of node names representing the path from valued nodes to the target.

    Raises
    ------
    ValueError
        If the node type is not supported.
    """
    if get_type(graph, target) == "standard":
        return get_path_to_standard(graph, target)
    elif get_type(graph, target) == "conditional":
        return get_path_to_conditional(graph, target)
    else:
        raise ValueError(
            "Getting the ancestors of nodes of type "
            + get_type(graph, target)
            + " is not supported"
        )


def get_path_to_standard(graph, node):
    """
    Get the path from the last valued nodes to a standard node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    node : str
        The name of the standard node.

    Returns
    -------
    set
        Set of node names representing the path from valued nodes to the standard node.
    """
    result = set((node,))
    if get_has_value(graph, node):
        return result
    dependencies = graph._nxdg.predecessors(node)
    for dependency in dependencies:
        result = result | get_path_to_target(graph, dependency)
    return result


def get_path_to_conditional(graph, conditional):
    """
    Get the path from the last valued nodes to a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    conditional : str
        The name of the conditional node.

    Returns
    -------
    set
        Set of node names representing the path from valued nodes to the conditional node.
    """
    result = set((conditional,))
    if get_has_value(graph, conditional):
        return result
    # If not, evaluate the conditions until one is found true
    for index, condition in enumerate(get_conditions(graph, conditional)):
        if get_has_value(graph, condition) and get_value(graph, condition):
            # A condition is true
            possibility = get_possibilities(graph, conditional)[index]
            result = result | get_path_to_standard(graph, condition)
            result = result | get_path_to_standard(graph, possibility)
            return result
    # If no conditions are true, we need to compute them, so all ancestors are in the path
    result = get_path_to_standard(graph, conditional)
    return result
