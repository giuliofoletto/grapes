"""
This module contains functions to simplify the graph, reducing the number of nodes or converting conditional to standard nodes.
"""

import networkx as nx

from . import function_composer
from .design import starting_node_properties
from .evaluate import execute_towards_all_conditions_of_conditional
from .features import (
    get_all_conditionals,
    get_all_sources,
    get_args,
    get_conditions,
    get_has_value,
    get_kwargs,
    get_possibilities,
    get_recipe,
    get_type,
    get_value,
    set_args,
    set_is_recipe,
    set_kwargs,
    set_recipe,
    set_value,
)


def simplify_dependency(graph, node, dependency):
    """
    Simplify a dependency of a node by merging its computation into that of the node.
    For example if the graph g is a->b->c and we simplify b as a dependency of c (calling simplify_dependency(g, c, b)), the graph becomes a->c, with c now computing what b used to compute as well.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    node : hashable (typically string)
        The name of the node that will include in its computation that of the dependency.
    dependency : hashable (typically string)
        The name of the dependency to eliminate and merge into the node.

    Raises
    ------
    TypeError
        If the dependency or its recipe is not a standard node.
    """
    # Make everything a keyword argument. This is the fate of a simplified node
    get_kwargs(graph, node).update(
        {argument: argument for argument in get_args(graph, node)}
    )
    # Build lists of dependencies
    func_dependencies = list(get_kwargs(graph, node).values())
    subfuncs = []
    subfuncs_dependencies = []
    for argument in get_kwargs(graph, node):
        if argument == dependency:
            if get_type(graph, dependency) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + dependency
                    + " is "
                    + get_type(graph, dependency)
                )
            if get_type(graph, get_recipe(graph, dependency)) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + get_recipe(graph, dependency)
                    + " is "
                    + get_type(graph, get_recipe(graph, dependency))
                )
            subfuncs.append(graph[get_recipe(graph, dependency)])  # Get python function
            subfuncs_dependencies.append(
                list(get_args(graph, dependency))
                + list(get_kwargs(graph, dependency).values())
            )
        else:
            subfuncs.append(function_composer.identity_token)
            subfuncs_dependencies.append([argument])
    # Compose the functions
    graph[get_recipe(graph, node)] = function_composer.function_compose_simple(
        graph[get_recipe(graph, node)],
        subfuncs,
        func_dependencies,
        subfuncs_dependencies,
    )
    # Change edges
    graph._nxdg.remove_edge(dependency, node)
    for argument in get_args(graph, dependency) + tuple(
        get_kwargs(graph, dependency).values()
    ):
        graph._nxdg.add_edge(argument, node, accessor=argument)
    # Update node
    set_args(graph, node, ())
    new_kwargs = get_kwargs(graph, node)
    new_kwargs.update(
        {
            argument: argument
            for argument in get_args(graph, dependency)
            + tuple(get_kwargs(graph, dependency).values())
        }
    )
    new_kwargs = {
        key: value for key, value in new_kwargs.items() if value != dependency
    }
    set_kwargs(graph, node, new_kwargs)


def simplify_all_dependencies(graph, node, exclude=set()):
    """
    Simplify all dependencies of a node except those in the exclude set.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    node : hashable (typically string)
        The name of the node to simplify.
    exclude : set or iterable, optional
        Dependencies to exclude from simplification. Default is empty set.
    """
    if not isinstance(exclude, set):
        exclude = set(exclude)
    # If a dependency is a source, it cannot be simplified
    exclude |= get_all_sources(graph)
    dependencies = get_args(graph, node) + tuple(get_kwargs(graph, node).values())
    for dependency in dependencies:
        if dependency not in exclude:
            simplify_dependency(graph, node, dependency)


def convert_conditional_to_trivial_step(
    graph, conditional, execute_towards_conditions=False
):
    """
    Convert a conditional node to a trivial step that returns the dependency corresponding to the true condition.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    conditional : hashable (typically string)
        The name of the conditional node to be converted.
    execute_towards_conditions : bool, optional
        Whether to execute the graph towards the conditions until one is found true. Default is False.

    Raises
    ------
    ValueError
        If no condition is true and there is no default possibility.
    """
    if execute_towards_conditions:
        execute_towards_all_conditions_of_conditional(graph, conditional)

    for index, condition in enumerate(get_conditions(graph, conditional)):
        if get_has_value(graph, condition) and get_value(graph, condition):
            break
    else:  # Happens if loop is never broken, i.e. when no conditions are true
        if (
            len(get_conditions(graph, conditional))
            == len(get_possibilities(graph, conditional)) - 1
        ):
            # We assume that the last possibility is considered a default
            index = -1
        else:
            raise ValueError(
                "Cannot convert conditional " + conditional + " if no condition is true"
            )
    # Get the correct possibility
    selected_possibility = get_possibilities(graph, conditional)[index]

    # Remove all previous edges (the correct one will be readded later)
    for condition in get_conditions(graph, conditional):
        graph._nxdg.remove_edge(condition, conditional)
    for possibility in get_possibilities(graph, conditional):
        graph._nxdg.remove_edge(possibility, conditional)
    # Rewrite node attributes
    nx.set_node_attributes(graph._nxdg, {conditional: starting_node_properties})
    # Add a trivial recipe
    recipe = "trivial_recipe_for_" + conditional
    set_recipe(graph, conditional, recipe)
    set_args(graph, conditional, (selected_possibility,))
    set_kwargs(graph, conditional, dict())

    # Add and connect the recipe
    # Avoid adding existing recipe so as not to overwrite attributes
    if recipe not in graph.nodes:
        graph._nxdg.add_node(recipe, **starting_node_properties)
    set_is_recipe(graph, recipe, True)
    graph._nxdg.add_edge(recipe, conditional)
    # Assign value of identity function to recipe
    set_value(graph, recipe, lambda x: x)

    # Add and connect the possibility
    graph._nxdg.add_edge(selected_possibility, conditional)


def convert_all_conditionals_to_trivial_steps(graph, execute_towards_conditions=False):
    """
    Convert all conditional nodes in the graph to trivial steps.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    execute_towards_conditions : bool, optional
        Whether to execute the graph towards the conditions until one is found true. Default is False.
    """
    conditionals = get_all_conditionals(graph)
    for conditional in conditionals:
        convert_conditional_to_trivial_step(
            graph, conditional, execute_towards_conditions
        )
