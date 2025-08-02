"""
Functions that manipulate the features of the graph.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import networkx as nx


def get_node_attribute(graph, node, attribute):
    attributes = graph.nodes[node]
    if attribute in attributes and attributes[attribute] is not None:
        return attributes[attribute]
    else:
        raise ValueError("Node " + node + " has no " + attribute)


def set_node_attribute(graph, node, attribute, value):
    graph.nodes[node][attribute] = value


def get_value(graph, node):
    if get_node_attribute(graph, node, "value") is not None and get_has_value(
        graph, node
    ):
        return get_node_attribute(graph, node, "value")
    else:
        raise ValueError("Node " + node + " has no value")


def set_value(graph, node, value):
    # Note: This changes reachability
    set_node_attribute(graph, node, "value", value)
    set_has_value(graph, node, True)


def unset_value(graph, node):
    # Note: This changes reachability
    set_has_value(graph, node, False)


def get_has_value(graph, node):
    return get_node_attribute(graph, node, "has_value")


def set_has_value(graph, node, has_value):
    return set_node_attribute(graph, node, "has_value", has_value)


def get_type(graph, node):
    return get_node_attribute(graph, node, "type")


def set_type(graph, node, type):
    return set_node_attribute(graph, node, "type", type)


def get_is_recipe(graph, node):
    return get_node_attribute(graph, node, "is_recipe")


def set_is_recipe(graph, node, is_recipe):
    return set_node_attribute(graph, node, "is_recipe", is_recipe)


def get_recipe(graph, node):
    return get_node_attribute(graph, node, "recipe")


def set_recipe(graph, node, recipe):
    return set_node_attribute(graph, node, "recipe", recipe)


def get_args(graph, node):
    return get_node_attribute(graph, node, "args")


def set_args(graph, node, args):
    return set_node_attribute(graph, node, "args", args)


def get_kwargs(graph, node):
    return get_node_attribute(graph, node, "kwargs")


def set_kwargs(graph, node, kwargs):
    return set_node_attribute(graph, node, "kwargs", kwargs)


def get_conditions(graph, node):
    conditions = get_node_attribute(graph, node, "conditions")
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return conditions


def set_conditions(graph, node, conditions):
    if not isinstance(conditions, list):
        conditions = list(conditions)
    return set_node_attribute(graph, node, "conditions", conditions)


def get_possibilities(graph, node):
    possibilities = get_node_attribute(graph, node, "possibilities")
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return possibilities


def set_possibilities(graph, node, possibilities):
    if not isinstance(possibilities, list):
        possibilities = list(possibilities)
    return set_node_attribute(graph, node, "possibilities", possibilities)


def get_is_frozen(graph, node):
    return get_node_attribute(graph, node, "is_frozen")


def set_is_frozen(graph, node, is_frozen):
    return set_node_attribute(graph, node, "is_frozen", is_frozen)


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


def get_topological_generation_index(graph, node):
    return get_node_attribute(graph, node, "topological_generation_index")


def set_topological_generation_index(graph, node, index):
    set_node_attribute(graph, node, "topological_generation_index", index)


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


def get_all_nodes(graph, exclude_recipes=False):
    nodes = set()
    for node in graph.nodes:
        if exclude_recipes and get_is_recipe(graph, node):
            continue
        nodes.add(node)
    return nodes


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
