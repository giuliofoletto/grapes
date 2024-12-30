"""
Functions to simplify the graph, reducing the number of nodes or converting conditional to standard nodes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
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


def simplify_dependency(graph, node_name, dependency_name):
    # Make everything a keyword argument. This is the fate of a simplified node
    get_kwargs(graph, node_name).update(
        {argument: argument for argument in get_args(graph, node_name)}
    )
    # Build lists of dependencies
    func_dependencies = list(get_kwargs(graph, node_name).values())
    subfuncs = []
    subfuncs_dependencies = []
    for argument in get_kwargs(graph, node_name):
        if argument == dependency_name:
            if get_type(graph, dependency_name) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + dependency_name
                    + " is "
                    + get_type(graph, dependency_name)
                )
            if get_type(graph, get_recipe(graph, dependency_name)) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + get_recipe(graph, dependency_name)
                    + " is "
                    + get_type(graph, get_recipe(graph, dependency_name))
                )
            subfuncs.append(
                graph[get_recipe(graph, dependency_name)]
            )  # Get python function
            subfuncs_dependencies.append(
                list(get_args(graph, dependency_name))
                + list(get_kwargs(graph, dependency_name).values())
            )
        else:
            subfuncs.append(function_composer.identity_token)
            subfuncs_dependencies.append([argument])
    # Compose the functions
    graph[get_recipe(graph, node_name)] = function_composer.function_compose_simple(
        graph[get_recipe(graph, node_name)],
        subfuncs,
        func_dependencies,
        subfuncs_dependencies,
    )
    # Change edges
    graph._nxdg.remove_edge(dependency_name, node_name)
    for argument in get_args(graph, dependency_name) + tuple(
        get_kwargs(graph, dependency_name).values()
    ):
        graph._nxdg.add_edge(argument, node_name, accessor=argument)
    # Update node
    set_args(graph, node_name, ())
    new_kwargs = get_kwargs(graph, node_name)
    new_kwargs.update(
        {
            argument: argument
            for argument in get_args(graph, dependency_name)
            + tuple(get_kwargs(graph, dependency_name).values())
        }
    )
    new_kwargs = {
        key: value for key, value in new_kwargs.items() if value != dependency_name
    }
    set_kwargs(graph, node_name, new_kwargs)


def simplify_all_dependencies(graph, node_name, exclude=set()):
    if not isinstance(exclude, set):
        exclude = set(exclude)
    # If a dependency is a source, it cannot be simplified
    exclude |= get_all_sources(graph)
    dependencies = get_args(graph, node_name) + tuple(
        get_kwargs(graph, node_name).values()
    )
    for dependency in dependencies:
        if dependency not in exclude:
            simplify_dependency(graph, node_name, dependency)


def convert_conditional_to_trivial_step(
    graph, conditional, execute_towards_conditions=False
):
    """
    Convert a conditional to a trivial step that returns the dependency corresponding to the true condition.

    Parameters
    ----------
    conditional: hashable (typically string)
        The name of the conditional node to be converted
    execute_towards_conditions: bool
        Whether to execute the graph towards the conditions until one is found true (default: False)
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
    Convert all conditionals in the graph to trivial steps that return the dependency corresponding to the true condition.

    Parameters
    ----------
    execute_towards_conditions: bool
        Whether to execute the graph towards the conditions until one is found true (default: False)
    """
    conditionals = get_all_conditionals(graph)
    for conditional in conditionals:
        convert_conditional_to_trivial_step(
            graph, conditional, execute_towards_conditions
        )
