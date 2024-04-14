"""
Functions to simplify the graph, reducing the number of nodes or converting conditional to standard nodes.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import networkx as nx

from . import function_composer
from .core import starting_node_properties
from .evaluate import execute_towards_all_conditions_of_conditional


def simplify_dependency(graph, node_name, dependency_name):
    # Make everything a keyword argument. This is the fate of a simplified node
    graph.get_kwargs(node_name).update(
        {argument: argument for argument in graph.get_args(node_name)}
    )
    # Build lists of dependencies
    func_dependencies = list(graph.get_kwargs(node_name).values())
    subfuncs = []
    subfuncs_dependencies = []
    for argument in graph.get_kwargs(node_name):
        if argument == dependency_name:
            if graph.get_type(dependency_name) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + dependency_name
                    + " is "
                    + graph.get_type(dependency_name)
                )
            if graph.get_type(graph.get_recipe(dependency_name)) != "standard":
                raise TypeError(
                    "Simplification only supports standard nodes, while the type of "
                    + graph.get_recipe(dependency_name)
                    + " is "
                    + graph.get_type(graph.get_recipe(dependency_name))
                )
            subfuncs.append(
                graph[graph.get_recipe(dependency_name)]
            )  # Get python function
            subfuncs_dependencies.append(
                list(graph.get_args(dependency_name))
                + list(graph.get_kwargs(dependency_name).values())
            )
        else:
            subfuncs.append(function_composer.identity_token)
            subfuncs_dependencies.append([argument])
    # Compose the functions
    graph[graph.get_recipe(node_name)] = function_composer.function_compose_simple(
        graph[graph.get_recipe(node_name)],
        subfuncs,
        func_dependencies,
        subfuncs_dependencies,
    )
    # Change edges
    graph._nxdg.remove_edge(dependency_name, node_name)
    for argument in graph.get_args(dependency_name) + tuple(
        graph.get_kwargs(dependency_name).values()
    ):
        graph._nxdg.add_edge(argument, node_name, accessor=argument)
    # Update node
    graph.set_args(node_name, ())
    new_kwargs = graph.get_kwargs(node_name)
    new_kwargs.update(
        {
            argument: argument
            for argument in graph.get_args(dependency_name)
            + tuple(graph.get_kwargs(dependency_name).values())
        }
    )
    new_kwargs = {
        key: value for key, value in new_kwargs.items() if value != dependency_name
    }
    graph.set_kwargs(node_name, new_kwargs)


def simplify_all_dependencies(graph, node_name, exclude=set()):
    if not isinstance(exclude, set):
        exclude = set(exclude)
    # If a dependency is a source, it cannot be simplified
    exclude |= graph.get_all_sources()
    dependencies = graph.get_args(node_name) + tuple(
        graph.get_kwargs(node_name).values()
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

    for index, condition in enumerate(graph.get_conditions(conditional)):
        if graph.has_value(condition) and graph.get_value(condition):
            break
    else:  # Happens if loop is never broken, i.e. when no conditions are true
        if (
            len(graph.get_conditions(conditional))
            == len(graph.get_possibilities(conditional)) - 1
        ):
            # We assume that the last possibility is considered a default
            index = -1
        else:
            raise ValueError(
                "Cannot convert conditional " + conditional + " if no condition is true"
            )
    # Get the correct possibility
    selected_possibility = graph.get_possibilities(conditional)[index]

    # Remove all previous edges (the correct one will be readded later)
    for condition in graph.get_conditions(conditional):
        graph._nxdg.remove_edge(condition, conditional)
    for possibility in graph.get_possibilities(conditional):
        graph._nxdg.remove_edge(possibility, conditional)
    # Rewrite node attributes
    nx.set_node_attributes(graph._nxdg, {conditional: starting_node_properties})
    # Add a trivial recipe
    recipe = "trivial_recipe_for_" + conditional
    graph.set_recipe(conditional, recipe)
    graph.set_args(conditional, (selected_possibility,))
    graph.set_kwargs(conditional, dict())

    # Add and connect the recipe
    # Avoid adding existing recipe so as not to overwrite attributes
    if recipe not in graph.nodes:
        graph._nxdg.add_node(recipe, **starting_node_properties)
    graph.set_is_recipe(recipe, True)
    graph._nxdg.add_edge(recipe, conditional)
    # Assign value of identity function to recipe
    graph.set_value(recipe, lambda x: x)

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
    conditionals = graph.get_all_conditionals()
    for conditional in conditionals:
        convert_conditional_to_trivial_step(
            graph, conditional, execute_towards_conditions
        )
