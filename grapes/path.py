"""
Functions to get the path needed to reach a target from valued nodes

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""


def get_path_to_target(graph, target):
    """
    Generic interface to get the path from the last valued nodes to a target.
    """
    if graph.get_type(target) == "standard":
        return get_path_to_standard(graph, target)
    elif graph.get_type(target) == "conditional":
        return get_path_to_conditional(graph, target)
    else:
        raise ValueError(
            "Getting the ancestors of nodes of type "
            + graph.get_type(target)
            + " is not supported"
        )


def get_path_to_standard(graph, node):
    """
    Get the path from the last valued nodes to a standard node.
    """
    result = set((node,))
    if graph.has_value(node):
        return result
    dependencies = graph._nxdg.predecessors(node)
    for dependency in dependencies:
        result = result | get_path_to_target(graph, dependency)
    return result


def get_path_to_conditional(graph, conditional):
    """
    Get the path from the last valued nodes to a conditional node.
    """
    result = set((conditional,))
    if graph.has_value(conditional):
        return result
    # If not, evaluate the conditions until one is found true
    for index, condition in enumerate(graph.get_conditions(conditional)):
        if graph.has_value(condition) and graph.get_value(condition):
            # A condition is true
            possibility = graph.get_possibilities(conditional)[index]
            result = result | get_path_to_standard(graph, condition)
            result = result | get_path_to_standard(graph, possibility)
            return result
    # If no conditions are true, we need to compute them, so all ancestors are in the path
    result = get_path_to_standard(graph, conditional)
    return result
