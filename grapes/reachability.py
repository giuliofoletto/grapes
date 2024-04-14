"""
Functions to operate the reachability of targets from valued nodes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""


def clear_reachabilities(graph, *args):
    """
    Clear reachabilities in the graph nodes.
    """
    if len(args) == 0:  # Interpret as "Clear everything"
        nodes_to_clear = graph.nodes
    else:
        nodes_to_clear = args & graph.nodes  # Intersection

    for node in nodes_to_clear:
        if graph.get_is_frozen(node):
            continue
        graph.unset_reachability(node)


def find_reachability_target(graph, target):
    """
    Generic interface to find the reachability of a GenericNode.
    """
    if graph.get_type(target) == "standard":
        return find_reachability_standard(graph, target)
    elif graph.get_type(target) == "conditional":
        return find_reachability_conditional(graph, target)
    else:
        raise ValueError(
            "Finding the reachability of nodes of type "
            + graph.get_type(target)
            + " is not supported"
        )


def find_reachability_standard(graph, node):
    """
    Find the reachability of a standard node.
    """
    # Check if it already has a reachability
    if graph.get_has_reachability(node):
        return
    # Check if it already has a value
    if graph.get_has_value(node):
        graph.set_reachability(node, "reachable")
        return
    # If not, check the missing dependencies of all arguments
    dependencies = set(graph._nxdg.predecessors(node))
    if len(dependencies) == 0:
        # If this node does not have predecessors (and does not have a value itgraph), it is not reachable
        graph.set_reachability(node, "unreachable")
        return
    # Otherwise, dependencies must be checked
    find_reachability_targets(graph, *dependencies)
    graph.set_reachability(node, get_worst_reachability(graph, *dependencies))


# Reachability
def find_reachability_conditional(graph, conditional):
    """
    Find the reachability of a conditional.
    """
    # Check if it already has a reachability
    if graph.get_has_reachability(conditional):
        return
    # Check if it already has a value
    if graph.get_has_value(conditional):
        graph.get_value(conditional)
        graph.set_reachability(conditional, "reachable")
        return
    # If not, evaluate the conditions until one is found true
    for index, condition in enumerate(graph.get_conditions(conditional)):
        if graph.get_has_value(condition) and graph.get_value(condition):
            # A condition is true
            possibility = graph.get_possibilities(conditional)[index]
            find_reachability_target(graph, possibility)
            graph.set_reachability(conditional, graph.get_reachability(possibility))
            return
    else:
        # Happens if loop is never broken, i.e. when no conditions are true
        # If all conditions and possibilities are reachable -> reachable
        # If all conditions and possibilities are unreachable -> unreachable
        # If some conditions are reachable or uncertain but the corresponding possibilities are all unreachable -> unreachable
        # In all other cases -> uncertain
        find_reachability_targets(graph, *graph.get_conditions(conditional))
        find_reachability_targets(graph, *graph.get_possibilities(conditional))

        if (
            get_worst_reachability(
                graph,
                *(
                    graph.get_conditions(conditional)
                    + graph.get_possibilities(conditional)
                )
            )
            == "reachable"
        ):
            # All conditions and possibilities are reachable -> reachable
            graph.set_reachability(conditional, "reachable")
        elif (
            get_best_reachability(
                graph,
                *(
                    graph.get_conditions(conditional)
                    + graph.get_possibilities(conditional)
                )
            )
            == "unreachable"
        ):
            # All conditions and possibilities are unreachable -> unreachable
            graph.set_reachability(conditional, "unreachable")
        else:
            not_unreachable_condition_possibilities = []
            for index, condition in enumerate(graph.get_conditions(conditional)):
                if graph.get_reachability(condition) != "unreachable":
                    not_unreachable_condition_possibilities.append(
                        graph.get_possibilities(conditional)[index]
                    )
            if (
                get_best_reachability(graph, *not_unreachable_condition_possibilities)
                == "unreachable"
            ):
                # All corresponding possibilities are unreachable -> unreachable
                graph.set_reachability(conditional, "unreachable")
            else:
                graph.set_reachability(conditional, "uncertain")


def find_reachability_targets(graph, *targets):
    for target in targets:
        find_reachability_target(graph, target)


def get_worst_reachability(graph, *nodes):
    list_of_reachabilities = []
    for node in nodes:
        list_of_reachabilities.append(graph.get_reachability(node))
    if "unreachable" in list_of_reachabilities:
        return "unreachable"
    elif "uncertain" in list_of_reachabilities:
        return "uncertain"
    else:
        return "reachable"


def get_best_reachability(graph, *nodes):
    list_of_reachabilities = []
    for node in nodes:
        list_of_reachabilities.append(graph.get_reachability(node))
    if "reachable" in list_of_reachabilities:
        return "reachable"
    elif "uncertain" in list_of_reachabilities:
        return "uncertain"
    else:
        return "unreachable"
