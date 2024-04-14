"""
Functions to evaluate the content of a graph, calling its recipes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .design import get_kwargs_values, get_list_of_values


def evaluate_target(graph, target, continue_on_fail=False):
    """
    Generic interface to evaluate a GenericNode.
    """
    if graph.get_type(target) == "standard":
        return evaluate_standard(graph, target, continue_on_fail)
    elif graph.get_type(target) == "conditional":
        return evaluate_conditional(graph, target, continue_on_fail)
    else:
        raise ValueError(
            "Evaluation of nodes of type "
            + graph.get_type(target)
            + " is not supported"
        )


def evaluate_standard(graph, node, continue_on_fail=False):
    """
    Evaluate of a node.
    """
    # Check if it already has a value
    if graph.get_has_value(node):
        graph.get_value(node)
        return
    # If not, evaluate all arguments
    for dependency_name in graph._nxdg.predecessors(node):
        evaluate_target(graph, dependency_name, continue_on_fail)

    # Actual computation happens here
    try:
        recipe = graph.get_recipe(node)
        func = graph.get_value(recipe)
        res = func(
            *get_list_of_values(graph, graph.get_args(node)),
            **get_kwargs_values(graph, graph.get_kwargs(node))
        )
    except Exception as e:
        if continue_on_fail:
            # Do nothing, we want to keep going
            return
        else:
            if len(e.args) > 0:
                e.args = ("While evaluating " + node + ": " + str(e.args[0]),) + e.args[
                    1:
                ]
            raise
    # Save results
    graph.set_value(node, res)


def evaluate_conditional(graph, conditional, continue_on_fail=False):
    """
    Evaluate a conditional.
    """
    # Check if it already has a value
    if graph.get_has_value(conditional):
        graph.get_value(conditional)
        return
    # If not, check if one of the conditions already has a true value
    for index, condition in enumerate(graph.get_conditions(conditional)):
        if graph.get_has_value(condition) and graph.get_value(condition):
            break
    else:
        # Happens only if loop is never broken
        # In this case, evaluate the conditions until one is found true
        for index, condition in enumerate(graph.get_conditions(conditional)):
            evaluate_target(graph, condition, continue_on_fail)
            if graph.get_has_value(condition) and graph.get_value(condition):
                break
            elif not graph.get_has_value(condition):
                # Computing failed
                if continue_on_fail:
                    # Do nothing, we want to keep going
                    return
                else:
                    raise ValueError("Node " + condition + " could not be computed")
        else:  # Happens if loop is never broken, i.e. when no conditions are true
            index = -1

    # Actual computation happens here
    try:
        possibility = graph.get_possibilities(conditional)[index]
        evaluate_target(graph, possibility, continue_on_fail)
        res = graph.get_value(possibility)
    except:
        if continue_on_fail:
            # Do nothing, we want to keep going
            return
        else:
            raise ValueError("Node " + possibility + " could not be computed")
    # Save results and release
    graph.set_value(conditional, res)


def execute_to_targets(graph, *targets):
    """
    Evaluate all nodes in the graph that are needed to reach the targets.
    """
    for target in targets:
        evaluate_target(graph, target, False)


def progress_towards_targets(graph, *targets):
    """
    Move towards the targets by evaluating nodes, but keep going if evaluation fails.
    """
    for target in targets:
        evaluate_target(graph, target, True)


def execute_towards_conditions(graph, *conditions):
    """
    Move towards the conditions, stop if one is found true.
    """
    for condition in conditions:
        evaluate_target(graph, condition, True)
        if graph.get_has_value(condition) and graph[condition]:
            break


def execute_towards_all_conditions_of_conditional(graph, conditional):
    """
    Move towards the conditions of a specific conditional, stop if one is found true.
    """
    execute_towards_conditions(graph, *graph.get_conditions(conditional))
