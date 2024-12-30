"""
Functions to evaluate the content of a graph, calling its recipes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .context import get_kwargs_values, get_list_of_values
from .features import (
    get_args,
    get_conditions,
    get_has_value,
    get_kwargs,
    get_possibilities,
    get_recipe,
    get_type,
    get_value,
    set_value,
)


def evaluate_target(graph, target, continue_on_fail=False):
    """
    Generic interface to evaluate a GenericNode.
    """
    if get_type(graph, target) == "standard":
        return evaluate_standard(graph, target, continue_on_fail)
    elif get_type(graph, target) == "conditional":
        return evaluate_conditional(graph, target, continue_on_fail)
    else:
        raise ValueError(
            "Evaluation of nodes of type "
            + get_type(graph, target)
            + " is not supported"
        )


def evaluate_standard(graph, node, continue_on_fail=False):
    """
    Evaluate of a node.
    """
    # Check if it already has a value
    if get_has_value(graph, node):
        get_value(graph, node)
        return
    # If not, evaluate all arguments
    for dependency_name in graph._nxdg.predecessors(node):
        evaluate_target(graph, dependency_name, continue_on_fail)

    # Actual computation happens here
    try:
        recipe = get_recipe(graph, node)
        func = get_value(graph, recipe)
        res = func(
            *get_list_of_values(graph, get_args(graph, node)),
            **get_kwargs_values(graph, get_kwargs(graph, node))
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
    set_value(graph, node, res)


def evaluate_conditional(graph, conditional, continue_on_fail=False):
    """
    Evaluate a conditional.
    """
    # Check if it already has a value
    if get_has_value(graph, conditional):
        get_value(graph, conditional)
        return
    # If not, check if one of the conditions already has a true value
    for index, condition in enumerate(get_conditions(graph, conditional)):
        if get_has_value(graph, condition) and get_value(graph, condition):
            break
    else:
        # Happens only if loop is never broken
        # In this case, evaluate the conditions until one is found true
        for index, condition in enumerate(get_conditions(graph, conditional)):
            evaluate_target(graph, condition, continue_on_fail)
            if get_has_value(graph, condition) and get_value(graph, condition):
                break
            elif not get_has_value(graph, condition):
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
        possibility = get_possibilities(graph, conditional)[index]
        evaluate_target(graph, possibility, continue_on_fail)
        res = get_value(graph, possibility)
    except:
        if continue_on_fail:
            # Do nothing, we want to keep going
            return
        else:
            raise ValueError("Node " + possibility + " could not be computed")
    # Save results and release
    set_value(graph, conditional, res)


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
        if get_has_value(graph, condition) and graph[condition]:
            break


def execute_towards_all_conditions_of_conditional(graph, conditional):
    """
    Move towards the conditions of a specific conditional, stop if one is found true.
    """
    execute_towards_conditions(graph, *get_conditions(graph, conditional))
