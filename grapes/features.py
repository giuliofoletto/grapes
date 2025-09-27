"""
This module contains functions that manipulate the features of the nodes.
"""

import networkx as nx


def get_node_attribute(graph, node, attribute):
    """
    Get the value of a specific attribute for a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    attribute : str
        The attribute to retrieve.

    Returns
    -------
    Any
        The value of the attribute.

    Raises
    ------
    ValueError
        If the attribute is not present or is None.
    """
    attributes = graph.nodes[node]
    if attribute in attributes and attributes[attribute] is not None:
        return attributes[attribute]
    else:
        raise ValueError("Node " + node + " has no " + attribute)


def set_node_attribute(graph, node, attribute, value):
    """
    Set the value of a specific attribute for a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    attribute : str
        The attribute to set.
    value : Any
        The value to assign.
    """
    graph.nodes[node][attribute] = value


def get_value(graph, node):
    """
    Get the value of a node if it has a value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    Any
        The value of the node.

    Raises
    ------
    ValueError
        If the node does not have a value.
    """
    if get_node_attribute(graph, node, "value") is not None and get_has_value(
        graph, node
    ):
        return get_node_attribute(graph, node, "value")
    else:
        raise ValueError("Node " + node + " has no value")


def set_value(graph, node, value):
    """
    Set the value of a node and mark it as having a value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    value : Any
        The value to assign.
    """
    # Note: This changes reachability
    set_node_attribute(graph, node, "value", value)
    set_has_value(graph, node, True)


def unset_value(graph, node):
    """
    Unset the value of a node and mark it as not having a value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    """
    # Note: This changes reachability
    set_has_value(graph, node, False)


def get_has_value(graph, node):
    """
    Check if a node has a value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    bool
        True if the node has a value, False otherwise.
    """
    return get_node_attribute(graph, node, "has_value")


def set_has_value(graph, node, has_value):
    """
    Set whether a node has a value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    has_value : bool
        Whether the node has a value.
    """
    return set_node_attribute(graph, node, "has_value", has_value)


def get_type(graph, node):
    """
    Get the type of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    str
        The type of the node.
    """
    return get_node_attribute(graph, node, "type")


def set_type(graph, node, type):
    """
    Set the type of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    type : str
        The type to assign.
    """
    return set_node_attribute(graph, node, "type", type)


def get_is_recipe(graph, node):
    """
    Check if a node is a recipe node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    bool
        True if the node is a recipe, False otherwise.
    """
    return get_node_attribute(graph, node, "is_recipe")


def set_is_recipe(graph, node, is_recipe):
    """
    Set whether a node is a recipe node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    is_recipe : bool
        Whether the node is a recipe.
    """
    return set_node_attribute(graph, node, "is_recipe", is_recipe)


def get_recipe(graph, node):
    """
    Get the recipe associated with a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    hashable (typically string)
        The name of the node that acts as recipe for the passed node.
    """
    return get_node_attribute(graph, node, "recipe")


def set_recipe(graph, node, recipe):
    """
    Set the recipe for a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    recipe : hashable (typically string)
        The name of the node that will act as recipe.
    """
    return set_node_attribute(graph, node, "recipe", recipe)


def get_args(graph, node):
    """
    Get the positional arguments for a node's recipe.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    list
        List of argument names.
    """
    return get_node_attribute(graph, node, "args")


def set_args(graph, node, args):
    """
    Set the positional arguments for a node's recipe.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    args : list
        List of argument names.
    """
    return set_node_attribute(graph, node, "args", args)


def get_kwargs(graph, node):
    """
    Get the keyword arguments for a node's recipe.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    dict
        Dictionary of keyword argument names and node names.
    """
    return get_node_attribute(graph, node, "kwargs")


def set_kwargs(graph, node, kwargs):
    """
    Set the keyword arguments for a node's recipe.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    kwargs : dict
        Dictionary of keyword argument names and node names.
    """
    return set_node_attribute(graph, node, "kwargs", kwargs)


def get_conditions(graph, node):
    """
    Get the conditions associated with a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    list
        List of condition node names.
    """
    conditions = get_node_attribute(graph, node, "conditions")
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return conditions


def set_conditions(graph, node, conditions):
    """
    Set the conditions for a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    conditions : list
        List of condition node names.
    """
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return set_node_attribute(graph, node, "conditions", conditions)


def get_possibilities(graph, node):
    """
    Get the possible outcomes associated with a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    list
        List of possible outcome node names.
    """
    possibilities = get_node_attribute(graph, node, "possibilities")
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return possibilities


def set_possibilities(graph, node, possibilities):
    """
    Set the possible outcomes for a conditional node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    possibilities : list
        List of possible outcome node names.
    """
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return set_node_attribute(graph, node, "possibilities", possibilities)


def get_is_frozen(graph, node):
    """
    Check if a node is frozen.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    bool
        True if the node is frozen, False otherwise.
    """
    return get_node_attribute(graph, node, "is_frozen")


def set_is_frozen(graph, node, is_frozen):
    """
    Set whether a node is frozen.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    is_frozen : bool
        Whether the node is frozen.
    """
    return set_node_attribute(graph, node, "is_frozen", is_frozen)


def freeze(graph, *args):
    """
    Freeze nodes in the graph, preventing their values from being changed.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *args : hashables (typically strings)
        Node names to freeze. If empty, all nodes are frozen.
    """
    if len(args) == 0:  # Interpret as "Freeze everything"
        nodes_to_freeze = graph.nodes
    else:
        nodes_to_freeze = args & graph.nodes  # Intersection

    for key in nodes_to_freeze:
        if get_has_value(graph, key):
            set_is_frozen(graph, key, True)


def unfreeze(graph, *args):
    """
    Unfreeze nodes in the graph, allowing their values to be changed.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    *args : hashables (typically strings)
        Node names to unfreeze. If empty, all nodes are unfrozen.
    """
    if len(args) == 0:  # Interpret as "Unfreeze everything"
        nodes_to_unfreeze = graph.nodes.keys()
    else:
        nodes_to_unfreeze = args & graph.nodes  # Intersection

    for key in nodes_to_unfreeze:
        set_is_frozen(graph, key, False)


def make_recipe_dependencies_also_recipes(graph):
    """
    Make dependencies (predecessors) of recipes also recipes, if they have only recipe successors.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
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


def get_topological_generation_index(graph, node):
    """
    Get the topological generation index of a node.
    It does not compute it, just retrieves the stored value.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.

    Returns
    -------
    int
        The topological generation index.
    """
    return get_node_attribute(graph, node, "topological_generation_index")


def set_topological_generation_index(graph, node, index):
    """
    Set the topological generation index of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the node.
    node : hashable (typically string)
        The name of the node.
    index : int
        The generation index to assign.
    """
    set_node_attribute(graph, node, "topological_generation_index", index)


def get_topological_order(graph):
    """
    Return list of nodes in topological order, i.e., from dependencies to targets.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.

    Returns
    -------
    list
        List of node names in topological order.
    """
    return list(nx.topological_sort(graph._nxdg))


def get_topological_generations(graph):
    """
    Return list of topological generations of the graph.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.

    Returns
    -------
    list
        List of generations, each generation is a list of node names.
    """
    return list(nx.topological_generations(graph._nxdg))


def compute_topological_generation_indexes(graph):
    """
    Compute and set the topological generation indexes for all nodes in the graph.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    """
    generations = get_topological_generations(graph)
    for node in graph.nodes:
        for index, generation in enumerate(generations):
            if node in generation:
                set_topological_generation_index(graph, node, index)
                break


def get_all_nodes(graph, exclude_recipes=False):
    """
    Get all nodes in the graph.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    exclude_recipes : bool, optional
        If True, exclude recipe nodes. Default is False.

    Returns
    -------
    set
        Set of node names.
    """
    nodes = set()
    for node in graph.nodes:
        if exclude_recipes and get_is_recipe(graph, node):
            continue
        nodes.add(node)
    return nodes


def get_all_sources(graph, exclude_recipes=False):
    """
    Get all source nodes in the graph (nodes with no incoming edges).

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    exclude_recipes : bool, optional
        If True, exclude recipe nodes. Default is False.

    Returns
    -------
    set
        Set of source node names.
    """
    sources = set()
    for node in graph.nodes:
        if exclude_recipes and get_is_recipe(graph, node):
            continue
        if graph._nxdg.in_degree(node) == 0:
            sources.add(node)
    return sources


def get_all_sinks(graph, exclude_recipes=False):
    """
    Get all sink nodes in the graph (nodes with no outgoing edges).

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    exclude_recipes : bool, optional
        If True, exclude recipe nodes. Default is False.

    Returns
    -------
    set
        Set of sink node names.
    """
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

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.

    Returns
    -------
    set
        Set of conditional node names.
    """
    conditionals = set()
    for node in graph.nodes:
        if get_type(graph, node) == "conditional":
            conditionals.add(node)
    return conditionals


def get_all_ancestors_target(graph, target):
    """
    Get all the ancestors of a node.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.
    target : str
        The name of the target node.

    Returns
    -------
    set
        Set of ancestor node names.
    """
    return nx.ancestors(graph._nxdg, target)


def get_all_recipes(graph):
    """
    Get all the recipe nodes in the graph.

    Parameters
    ----------
    graph : grapes Graph
        The graph containing the nodes.

    Returns
    -------
    set
        Set of recipe node names.
    """
    recipes = set()
    for node in graph.nodes:
        if get_is_recipe(graph, node):
            recipes.add(node)
    return recipes
