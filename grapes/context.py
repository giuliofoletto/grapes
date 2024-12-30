"""
Functions that manipulate the context of the graph.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from .features import (
    get_has_value,
    get_is_frozen,
    get_is_recipe,
    get_value,
    set_value,
    unset_value,
)


# Context
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


# Context
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


# Context
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


# Context
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


# Context
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


# Context
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


# Context
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
