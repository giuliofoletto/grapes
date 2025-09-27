"""
This module contains functions that manipulate the context of the graph, i.e., the values assigned to its nodes.
"""

import inspect

from .features import (
    get_has_value,
    get_is_frozen,
    get_is_recipe,
    get_value,
    set_value,
    unset_value,
)


def clear_values(graph, *args):
    """
    Clear (i.e. erase) values in the graph nodes.

    Parameters
    ----------
    graph : grapes Graph
        The graph whose values are to be cleared.
    *args : hashables (typically strings)
        Names of nodes whose values are to be cleared. If no names are given, all values are cleared.

    Notes
    -----
    Frozen nodes are not cleared.
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
    Update the internal context with a dictionary.

    Parameters
    ----------
    graph : grapes Graph
        The graph to update.
    dictionary : dict
        Dictionary with the new values. Keys are node names, values are the values to assign to those nodes.

    Notes
    -----
    Only keys that are already nodes in the graph are considered.
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
    graph : grapes Graph
        The graph to update.
    dictionary : dict
        Dictionary with the new values.

    Notes
    -----
    Only keys that are already nodes in the graph are considered.
    Frozen nodes are not cleared.
    """
    clear_values(graph)
    update_internal_context(graph, dictionary)


def get_internal_context(graph, exclude_recipes=False):
    """
    Get the internal context.

    Parameters
    ----------
    graph : grapes Graph
        The graph whose context is to be retrieved.
    exclude_recipes : bool
        Whether to exclude recipes from the returned dictionary or keep them, default: False.

    Returns
    -------
    dict
        Dictionary with the current values of the graph nodes.
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
    Get list of values corresponding to list of keys.

    Parameters
    ----------
    graph : grapes Graph
        The graph from which to get the values.
    list_of_keys : list of hashables (typically strings)
        List of names of nodes whose values are required.

    Returns
    -------
    list
        List like list_of_keys which contains values of nodes.
    """
    res = []
    for key in list_of_keys:
        res.append(get_value(graph, key))
    return res


def get_dict_of_values(graph, list_of_keys):
    """
    Get dictionary of key:value pairs corresponding to list of keys.

    Parameters
    ----------
    graph : grapes Graph
        The graph from which to get the values.
    list_of_keys : list of hashables (typically strings)
        List of names of nodes whose values are required.

    Returns
    -------
    dict
        Dictionary whose keys are the elements of list_of_keys and whose values are the corresponding node values.
    """
    return {key: get_value(graph, key) for key in list_of_keys}


def get_kwargs_values(graph, dictionary):
    """
    Get values from the graph, using a dictionary that works like function kwargs.

    Parameters
    ----------
    graph : grapes Graph
        The graph from which to get the values.
    dictionary : dict
        Dictionary whose keys are to be interpreted as keys for function kwargs, while values in dictionary are node names.

    Returns
    -------
    dict
        A dict with the same keys of the input dictionary, but with values replaced by the values of the nodes.
    """
    return {key: get_value(graph, value) for key, value in dictionary.items()}


def update_recipes_from_module(graph, module):
    """
    Update the internal context to assign to recipes the functions with the same name taken from a module.

    Parameters
    ----------
    graph : grapes Graph
        The graph to update.
    module : module
        Module from which to load the functions.

    Notes
    -----
    Only functions whose name matches a recipe in the graph are loaded.
    """
    context = {
        name: func
        for name, func in inspect.getmembers(module, predicate=inspect.isfunction)
    }
    update_internal_context(graph, context)
