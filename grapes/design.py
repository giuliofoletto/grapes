"""
Functions to design the graph and get its features.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import inspect

import networkx as nx

from .core import (
    get_has_value,
    get_is_frozen,
    get_is_recipe,
    get_type,
    get_value,
    set_args,
    set_conditions,
    set_has_value,
    set_is_frozen,
    set_is_recipe,
    set_kwargs,
    set_possibilities,
    set_recipe,
    set_topological_generation_index,
    set_type,
    set_value,
    starting_node_properties,
    unset_value,
)


def add_step(graph, name, recipe=None, *args, **kwargs):
    """
    Interface to add a node to the graph, with all its dependencies.
    """
    # Check that if a node has dependencies, it also has a recipe
    if recipe is None and (len(args) > 0 or len(kwargs.keys()) > 0):
        raise ValueError("Cannot add node with dependencies without a recipe")

    elif recipe is None:  # Accept nodes with no dependencies
        # Avoid adding existing node so as not to overwrite attributes
        if name not in graph.nodes:
            graph._nxdg.add_node(name, **starting_node_properties)

    else:  # Standard case
        # Add the node
        # Avoid adding existing node so as not to overwrite attributes
        if name not in graph.nodes:
            graph._nxdg.add_node(name, **starting_node_properties)
        # Set attributes
        # Note: This could be done in the constructor, but doing it separately adds flexibility
        # Indeed, we might want to change how attributes work, and we can do it by modifying setters
        set_recipe(graph, name, recipe)
        set_args(graph, name, args)
        set_kwargs(graph, name, kwargs)

        # Add and connect the recipe
        # Avoid adding existing recipe so as not to overwrite attributes
        if recipe not in graph.nodes:
            graph._nxdg.add_node(recipe, **starting_node_properties)
        set_is_recipe(graph, recipe, True)
        # Note: adding argument to the edges is elegant but impractical.
        # If relations were defined through edges attributes rather than stored inside nodes,
        # retrieving them would require iterating through all edges and selecting the ones with the right attributes.
        # Although feasible, this is much slower than simply accessing node attributes.
        graph._nxdg.add_edge(recipe, name)

        # Add and connect the other dependencies
        for arg in args:
            # Avoid adding existing dependencies so as not to overwrite attributes
            if arg not in graph.nodes:
                graph._nxdg.add_node(arg, **starting_node_properties)
            graph._nxdg.add_edge(arg, name)
        for value in kwargs.values():
            # Avoid adding existing dependencies so as not to overwrite attributes
            if value not in graph.nodes:
                graph._nxdg.add_node(value, **starting_node_properties)
            graph._nxdg.add_edge(value, name)


def add_step_quick(graph, name, recipe):
    """
    Interface to quickly add a step by passing a name and a function.

    The recipe node takes the name of the passed function.
    Dependency nodes are built from the args and kwonlyargs of the passed function.
    """
    # Check that the passed recipe is a valid function
    if not inspect.isfunction(recipe):
        raise TypeError(
            "The passed recipe should be a function, but it is a " + type(recipe)
        )
    argspec = inspect.getfullargspec(recipe)
    # varargs and varkw are not supported because add_step_quick needs parameter names to build nodes
    if argspec.varargs is not None or argspec.varkw is not None:
        raise ValueError(
            "Functions with varargs or varkwargs are not supported by add_step_quick because there would be no way to name dependency nodes"
        )

    # Get function name and parameters
    recipe_name = recipe.__name__
    # Lambdas are all automatically named "<lambda>" so we change this
    if recipe_name == "<lambda>":
        recipe_name = "recipe_for_" + name
    args = argspec.args
    kwargs_list = argspec.kwonlyargs
    # Build a dictionary with identical keys and values so that recipe is called all the keys are used are kwargs
    kwargs = {kw: kw for kw in kwargs_list}
    # Add the step: this will create nodes for name, recipe_name and all elements of args and kwargs_list
    add_step(graph, name, recipe_name, *args, **kwargs)
    # Directly set the value of recipe_name to recipe
    set_value(graph, recipe_name, recipe)


def add_simple_conditional(graph, name, condition, value_true, value_false):
    """
    Interface to add a conditional to the graph.
    """
    add_multiple_conditional(
        graph, name, conditions=[condition], possibilities=[value_true, value_false]
    )


def add_multiple_conditional(graph, name, conditions, possibilities):
    """
    Interface to add a multiple conditional to the graph.
    """
    # Add all nodes and connect all edges
    # Avoid adding existing node so as not to overwrite attributes
    if name not in graph.nodes:
        graph._nxdg.add_node(name, **starting_node_properties)
    for node in conditions + possibilities:
        # Avoid adding existing dependencies so as not to overwrite attributes
        if node not in graph.nodes:
            graph._nxdg.add_node(node, **starting_node_properties)
        graph._nxdg.add_edge(node, name)

    # Specify that this node is a conditional
    set_type(graph, name, "conditional")

    # Add conditions name to the list of conditions of the conditional
    set_conditions(graph, name, conditions)

    # Add possibilities to the list of possibilities of the conditional
    set_possibilities(graph, name, possibilities)


def edit_step(graph, name, recipe=None, *args, **kwargs):
    """
    Interface to edit an existing node, changing its predecessors
    """
    if name not in graph.nodes:
        raise ValueError("Cannot edit non-existent node " + name)

    # Store old attributes
    was_recipe = get_is_recipe(graph, name)
    was_frozen = get_is_frozen(graph, name)
    had_value = get_has_value(graph, name)
    if had_value:
        old_value = get_value(graph, name)

    # Remove in-edges from the node because we need to replace them
    # use of list() is to make a copy because in_edges() returns a view
    graph._nxdg.remove_edges_from(list(graph._nxdg.in_edges(name)))
    # Readd the step. This should not break anything
    add_step(graph, name, recipe, *args, **kwargs)

    # Readd attributes
    # Readding out-edges is not needed because we never removed them
    set_is_recipe(graph, name, was_recipe)
    set_is_frozen(graph, name, was_frozen)
    set_has_value(graph, name, had_value)
    if had_value:
        set_value(graph, name, old_value)


def remove_step(graph, name):
    """
    Interface to remove an existing node, without changing anything else
    """
    if name not in graph.nodes:
        raise ValueError("Cannot edit non-existent node " + name)
    graph._nxdg.remove_node(name)


def clear_values(graph, *args):
    """
    Clear values in the graph nodes.
    """
    if len(args) == 0:  # Interpret as "Clear everything"
        nodes_to_clear = graph.nodes
    else:
        nodes_to_clear = args & graph.nodes  # Intersection

    for node in nodes_to_clear:
        if get_is_frozen(graph, node):
            continue
        unset_value(graph, node)


def update_internal_context(graph, dictionary):
    """
    Update internal context with a dictionary.

    Parameters
    ----------
    dictionary: dict
        Dictionary with the new values
    """
    for key, value in dictionary.items():
        # Accept dictionaries with more keys than needed
        if key in graph.nodes:
            set_value(graph, key, value)


def set_internal_context(graph, dictionary):
    """
    Clear all values and then set a new internal context with a dictionary.

    Parameters
    ----------
    dictionary: dict
        Dictionary with the new values
    """
    clear_values(graph)
    update_internal_context(graph, dictionary)


def get_internal_context(graph, exclude_recipes=False):
    """
    Get the internal context.

    Parameters
    ----------
    exclude_recipes: bool
        Whether to exclude recipes from the returned dictionary or keep them.
    """
    if exclude_recipes:
        return {
            key: get_value(graph, key)
            for key in graph.nodes
            if (get_has_value(graph, key) and not get_is_recipe(graph, key))
        }
    else:
        return {
            key: get_value(graph, key)
            for key in graph.nodes
            if get_has_value(graph, key)
        }


def get_list_of_values(graph, list_of_keys):
    """
    Get values as list.

    Parameters
    ----------
    list_of_keys: list of hashables (typically strings)
        List of names of nodes whose values are required

    Returns
    -------
    list
        List like list_of_keys which contains values of nodes
    """
    res = []
    for key in list_of_keys:
        res.append(get_value(graph, key))
    return res


def get_dict_of_values(graph, list_of_keys):
    """
    Get values as dictionary.

    Parameters
    ----------
    list_of_keys: list of hashables (typically strings)
        List of names of nodes whose values are required

    Returns
    -------
    dict
        Dictionary whose keys are the elements of list_of_keys and whose values are the corresponding node values
    """
    return {key: get_value(graph, key) for key in list_of_keys}


def get_kwargs_values(graph, dictionary):
    """
    Get values from the graph, using a dictionary that works like function kwargs.

    Parameters
    ----------
    dictionary: dict
        Keys in dictionary are to be interpreted as keys for function kwargs, while values in dictionary are node names

    Returns
    -------
    dict
        A dict with the same keys of the input dictionary, but with values replaced by the values of the nodes
    """
    return {key: get_value(graph, value) for key, value in dictionary.items()}


def freeze(graph, *args):
    if len(args) == 0:  # Interpret as "Freeze everything"
        nodes_to_freeze = graph.nodes
    else:
        nodes_to_freeze = args & graph.nodes  # Intersection

    for key in nodes_to_freeze:
        if get_has_value(graph, key):
            set_is_frozen(graph, key, True)


def unfreeze(graph, *args):
    if len(args) == 0:  # Interpret as "Unfreeze everything"
        nodes_to_unfreeze = graph.nodes.keys()
    else:
        nodes_to_unfreeze = args & graph.nodes  # Intersection

    for key in nodes_to_unfreeze:
        set_is_frozen(graph, key, False)


def make_recipe_dependencies_also_recipes(graph):
    """
    Make dependencies (predecessors) of recipes also recipes, if they have only recipe successors
    """
    # Work in reverse topological order, to get successors before predecessors
    for node in reversed(get_topological_order(graph)):
        if get_is_recipe(graph, node):
            for parent in graph._nxdg.predecessors(node):
                if not get_is_recipe(graph, parent):
                    all_children_are_recipes = True
                    for child in graph._nxdg.successors(parent):
                        if not get_is_recipe(graph, child):
                            all_children_are_recipes = False
                            break
                    if all_children_are_recipes:
                        set_is_recipe(graph, parent, True)


def finalize_definition(graph):
    """
    Perform operations that should typically be done after the definition of a graph is completed

    Currently, this freezes all values, because it is assumed that values given during definition are to be frozen.
    It also marks dependencies of recipes as recipes themselves.
    """
    make_recipe_dependencies_also_recipes(graph)
    update_topological_generation_indexes(graph)
    freeze(graph)


def get_topological_order(graph):
    """
    Return list of nodes in topological order, i.e., from dependencies to targets
    """
    return list(nx.topological_sort(graph._nxdg))


def get_topological_generations(graph):
    """
    Return list of topological generations of the graph
    """
    return list(nx.topological_generations(graph._nxdg))


def update_topological_generation_indexes(graph):
    generations = get_topological_generations(graph)
    for node in graph.nodes:
        for index, generation in enumerate(generations):
            if node in generation:
                set_topological_generation_index(graph, node, index)
                break


def get_all_sources(graph, exclude_recipes=False):
    sources = set()
    for node in graph.nodes:
        if exclude_recipes and get_is_recipe(graph, node):
            continue
        if graph._nxdg.in_degree(node) == 0:
            sources.add(node)
    return sources


def get_all_sinks(graph, exclude_recipes=False):
    sinks = set()
    for node in graph.nodes:
        if exclude_recipes and get_is_recipe(graph, node):
            continue
        if graph._nxdg.out_degree(node) == 0:
            sinks.add(node)
    return sinks


def get_all_conditionals(graph):
    """
    Get set of all conditional nodes in the graph.
    """
    conditionals = set()
    for node in graph.nodes:
        if get_type(graph, node) == "conditional":
            conditionals.add(node)
    return conditionals


def get_all_ancestors_target(graph, target):
    """
    Get all the ancestors of a node.
    """
    return nx.ancestors(graph._nxdg, target)
