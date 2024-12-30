"""
Functions to operate the reachability of targets from valued nodes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .core import (
    get_conditions,
    get_has_value,
    get_node_attribute,
    get_possibilities,
    get_type,
    get_value,
    set_node_attribute,
)
from .design import get_is_frozen


def get_has_reachability(graph, node):
    return get_node_attribute(graph, node, "has_reachability")


def set_has_reachability(graph, node, has_reachability):
    return set_node_attribute(graph, node, "has_reachability", has_reachability)


def get_reachability(graph, node):
    if get_node_attribute(
        graph, node, "reachability"
    ) is not None and get_node_attribute(graph, node, "has_reachability"):
        return get_node_attribute(graph, node, "reachability")
    else:
        raise ValueError("Node " + node + " has no reachability")


def set_reachability(graph, node, reachability):
    if reachability not in ("unreachable", "uncertain", "reachable"):
        raise ValueError(reachability + " is not a valid reachability value.")
    set_node_attribute(graph, node, "reachability", reachability)
    set_node_attribute(graph, node, "has_reachability", True)


def unset_reachability(graph, node):
    set_node_attribute(graph, node, "has_reachability", False)


def clear_reachabilities(graph, *args):
    """
    Clear reachabilities in the graph nodes.
    """
    if len(args) == 0:  # Interpret as "Clear everything"
        nodes_to_clear = graph.nodes
    else:
        nodes_to_clear = args & graph.nodes  # Intersection

    for node in nodes_to_clear:
        if get_is_frozen(graph, node):
            continue
        unset_reachability(graph, node)


def find_reachability_target(graph, target):
    """
    Generic interface to find the reachability of a GenericNode.
    """
    if get_type(graph, target) == "standard":
        return find_reachability_standard(graph, target)
    elif get_type(graph, target) == "conditional":
        return find_reachability_conditional(graph, target)
    else:
        raise ValueError(
            "Finding the reachability of nodes of type "
            + get_type(graph, target)
            + " is not supported"
        )


def find_reachability_standard(graph, node):
    """
    Find the reachability of a standard node.
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
    find_reachability_targets(graph, *dependencies)
    set_reachability(graph, node, get_worst_reachability(graph, *dependencies))


# Reachability
def find_reachability_conditional(graph, conditional):
    """
    Find the reachability of a conditional.
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
            find_reachability_target(graph, possibility)
            set_reachability(graph, conditional, get_reachability(graph, possibility))
            return
    else:
        # Happens if loop is never broken, i.e. when no conditions are true
        # If all conditions and possibilities are reachable -> reachable
        # If all conditions and possibilities are unreachable -> unreachable
        # If some conditions are reachable or uncertain but the corresponding possibilities are all unreachable -> unreachable
        # In all other cases -> uncertain
        find_reachability_targets(graph, *get_conditions(graph, conditional))
        find_reachability_targets(graph, *get_possibilities(graph, conditional))

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


def find_reachability_targets(graph, *targets):
    for target in targets:
        find_reachability_target(graph, target)


def get_worst_reachability(graph, *nodes):
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
    list_of_reachabilities = []
    for node in nodes:
        list_of_reachabilities.append(get_reachability(graph, node))
    if "reachable" in list_of_reachabilities:
        return "reachable"
    elif "uncertain" in list_of_reachabilities:
        return "uncertain"
    else:
        return "unreachable"
