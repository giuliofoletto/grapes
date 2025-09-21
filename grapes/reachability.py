"""
Functions to operate the reachability of targets from valued nodes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .features import (
    get_conditions,
    get_has_value,
    get_is_frozen,
    get_node_attribute,
    get_possibilities,
    get_type,
    get_value,
    set_node_attribute,
)


def get_has_reachability(graph, node):
    """
    Check if a node has a reachability value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the node.

    Returns
    -------
    bool
        True if the node has a reachability value, False otherwise.
    """
    return get_node_attribute(graph, node, "has_reachability")


def set_has_reachability(graph, node, has_reachability):
    """
    Set whether a node has a reachability value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the node.
    has_reachability : bool
        Whether the node has a reachability value.
    """
    return set_node_attribute(graph, node, "has_reachability", has_reachability)


def get_reachability(graph, node):
    """
    Get the reachability value of a node.
    It does not compute it, just retrieves it.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the node.

    Returns
    -------
    str
        The reachability value ("unreachable", "uncertain", or "reachable").

    Raises
    ------
    ValueError
        If the node does not have a reachability value.
    """
    if get_node_attribute(
        graph, node, "reachability"
    ) is not None and get_node_attribute(graph, node, "has_reachability"):
        return get_node_attribute(graph, node, "reachability")
    else:
        raise ValueError("Node " + node + " has no reachability")


def set_reachability(graph, node, reachability):
    """
    Set the reachability value of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the node.
    reachability : str
        The reachability value ("unreachable", "uncertain", or "reachable").

    Raises
    ------
    ValueError
        If the reachability value is not valid.
    """
    if reachability not in ("unreachable", "uncertain", "reachable"):
        raise ValueError(reachability + " is not a valid reachability value.")
    set_node_attribute(graph, node, "reachability", reachability)
    set_node_attribute(graph, node, "has_reachability", True)


def unset_reachability(graph, node):
    """
    Unset the reachability value of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the node.
    """
    set_node_attribute(graph, node, "has_reachability", False)


def clear_reachabilities(graph, *args):
    """
    Clear reachabilities in the graph nodes.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *args : str
        Node names to clear. If empty, all nodes are cleared.
    """
    if len(args) == 0:  # Interpret as "Clear everything"
        nodes_to_clear = graph.nodes
    else:
        nodes_to_clear = args & graph.nodes  # Intersection

    for node in nodes_to_clear:
        if get_is_frozen(graph, node):
            continue
        unset_reachability(graph, node)


def compute_reachability_target(graph, target):
    """
    Compute the reachability of a target node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    target : str
        The name of the target node.

    Raises
    ------
    ValueError
        If the node type is not supported.
    """
    if get_type(graph, target) == "standard":
        return compute_reachability_standard(graph, target)
    elif get_type(graph, target) == "conditional":
        return compute_reachability_conditional(graph, target)
    else:
        raise ValueError(
            "Computing the reachability of nodes of type "
            + get_type(graph, target)
            + " is not supported"
        )


def compute_reachability_standard(graph, node):
    """
    Compute the reachability of a standard node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : str
        The name of the standard node.
    """
    # Check if it already has a reachability
    if get_has_reachability(graph, node):
        return
    # Check if it already has a value
    if get_has_value(graph, node):
        set_reachability(graph, node, "reachable")
        return
    # If not, check the missing dependencies of all arguments
    dependencies = set(graph._nxdg.predecessors(node))
    if len(dependencies) == 0:
        # If this node does not have predecessors (and does not have a value itgraph), it is not reachable
        set_reachability(graph, node, "unreachable")
        return
    # Otherwise, dependencies must be checked
    compute_reachability_targets(graph, *dependencies)
    set_reachability(graph, node, get_worst_reachability(graph, *dependencies))


def compute_reachability_conditional(graph, conditional):
    """
    Compute the reachability of a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    conditional : str
        The name of the conditional node.
    """
    # Check if it already has a reachability
    if get_has_reachability(graph, conditional):
        return
    # Check if it already has a value
    if get_has_value(graph, conditional):
        get_value(graph, conditional)
        set_reachability(graph, conditional, "reachable")
        return
    # If not, evaluate the conditions until one is found true
    for index, condition in enumerate(get_conditions(graph, conditional)):
        if get_has_value(graph, condition) and get_value(graph, condition):
            # A condition is true
            possibility = get_possibilities(graph, conditional)[index]
            compute_reachability_target(graph, possibility)
            set_reachability(graph, conditional, get_reachability(graph, possibility))
            return
    else:
        # Happens if loop is never broken, i.e. when no conditions are true
        # If all conditions and possibilities are reachable -> reachable
        # If all conditions and possibilities are unreachable -> unreachable
        # If some conditions are reachable or uncertain but the corresponding possibilities are all unreachable -> unreachable
        # In all other cases -> uncertain
        compute_reachability_targets(graph, *get_conditions(graph, conditional))
        compute_reachability_targets(graph, *get_possibilities(graph, conditional))

        if (
            get_worst_reachability(
                graph,
                *(
                    get_conditions(graph, conditional)
                    + get_possibilities(graph, conditional)
                )
            )
            == "reachable"
        ):
            # All conditions and possibilities are reachable -> reachable
            set_reachability(graph, conditional, "reachable")
        elif (
            get_best_reachability(
                graph,
                *(
                    get_conditions(graph, conditional)
                    + get_possibilities(graph, conditional)
                )
            )
            == "unreachable"
        ):
            # All conditions and possibilities are unreachable -> unreachable
            set_reachability(graph, conditional, "unreachable")
        else:
            not_unreachable_condition_possibilities = []
            for index, condition in enumerate(get_conditions(graph, conditional)):
                if get_reachability(graph, condition) != "unreachable":
                    not_unreachable_condition_possibilities.append(
                        get_possibilities(graph, conditional)[index]
                    )
            if (
                get_best_reachability(graph, *not_unreachable_condition_possibilities)
                == "unreachable"
            ):
                # All corresponding possibilities are unreachable -> unreachable
                set_reachability(graph, conditional, "unreachable")
            else:
                set_reachability(graph, conditional, "uncertain")


def compute_reachability_targets(graph, *targets):
    """
    Compute the reachability of multiple target nodes.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *targets : str
        Node names to check reachability for.
    """
    for target in targets:
        compute_reachability_target(graph, target)


def get_worst_reachability(graph, *nodes):
    """
    Get the worst (least reachable) reachability value among a set of nodes.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *nodes : str
        Node names to check.

    Returns
    -------
    str
        The worst reachability value ("unreachable", "uncertain", or "reachable").
    """
    list_of_reachabilities = []
    for node in nodes:
        list_of_reachabilities.append(get_reachability(graph, node))
    if "unreachable" in list_of_reachabilities:
        return "unreachable"
    elif "uncertain" in list_of_reachabilities:
        return "uncertain"
    else:
        return "reachable"


def get_best_reachability(graph, *nodes):
    """
    Get the best (most reachable) reachability value among a set of nodes.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *nodes : str
        Node names to check.

    Returns
    -------
    str
        The best reachability value ("reachable", "uncertain", or "unreachable").
    """
    list_of_reachabilities = []
    for node in nodes:
        list_of_reachabilities.append(get_reachability(graph, node))
    if "reachable" in list_of_reachabilities:
        return "reachable"
    elif "uncertain" in list_of_reachabilities:
        return "uncertain"
    else:
        return "unreachable"
