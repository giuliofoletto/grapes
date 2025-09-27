"""
This module contains functions to design the graph.
"""

import inspect

from .features import (
    freeze,
    get_has_value,
    get_is_frozen,
    get_is_recipe,
    get_value,
    make_recipe_dependencies_also_recipes,
    set_args,
    set_conditions,
    set_has_value,
    set_is_frozen,
    set_is_recipe,
    set_kwargs,
    set_possibilities,
    set_recipe,
    set_type,
    set_value,
    compute_topological_generation_indexes,
)

starting_node_properties = {
    "type": "standard",
    "has_value": False,
    "value": None,
    "is_frozen": False,
    "is_recipe": False,
    "topological_generation_index": -1,
    "has_reachability": False,
    "reachability": None,
}


def add_step(graph, name, recipe=None, *args, **kwargs):
    """
    Interface to add a node to the graph, with all its dependencies.

    Parameters
    ----------
    graph : grapes Graph
        The graph to which the step is to be added.
    name : hashable (typically string)
        Name of the node to add.
    recipe : hashable (typically string), optional
        Name of the recipe node to add, if any. Default is None.
    *args : hashables (typically strings)
        Names of nodes to add as positional dependencies.
    **kwargs : hashables (typically strings)
        Names of nodes to add as keyword dependencies. Keys in the dicts are the keywords to be used when calling the recipe.

    Raises
    ------
    ValueError
        If a node with dependencies is added without a recipe.
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

    Parameters
    ----------
    graph : grapes Graph
        The graph to which to add the step.
    name : hashable (typically string)
        Name of the node to add.
    recipe : function
        Function to be used as recipe.

    Raises
    ------
    TypeError
        If the passed recipe is not a function.
    ValueError
        If the passed function has varargs or varkwargs, which are not supported.

    Notes
    -----
    If the function is unnamed (i.e. a lambda), it is automatically renamed to "recipe_for_" + name.
    """
    # Check that the passed recipe is a valid function
    if not inspect.isfunction(recipe):
        raise TypeError(
            "The passed recipe should be a function, but it is a " + str(type(recipe))
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
    A conditional is a node that takes the value of another node (one of the possibilities) depending on the boolean value of a condition node.

    Parameters
    ----------
    graph : grapes Graph
        The graph to which to add the conditional.
    name : hashable (typically string)
        Name of the conditional node to add.
    condition : hashable (typically string)
        Name of the condition node to add.
        The condition node controls which of the possibility nodes passes its value to the conditional.
    value_true : hashable (typically string)
        Name of the node to add as possibility if the condition is true.
    value_false : hashable (typically string)
        Name of the node to add as possibility if the condition is false.
    """
    add_multiple_conditional(
        graph, name, conditions=[condition], possibilities=[value_true, value_false]
    )


def add_multiple_conditional(graph, name, conditions, possibilities):
    """
    Interface to add a multiple conditional to the graph.
    A multiple conditional is a node that takes the value of one of its possibilities depending on which of its condition nodes evaluates to True.

    Parameters
    ----------
    graph : grapes Graph
        The graph to which to add the conditional.
    name : hashable (typically string)
        Name of the conditional node to add.
    conditions : list of hashables (typically strings)
        Names of the condition nodes to add.
    possibilities : list of hashables (typically strings)
        Names of the nodes to add as possibilities.

    Raises
    ------
    ValueError
        If the number of possibilities is not equal to the number of conditions or to the number of conditions plus one (to allow for a default possibility).
    """
    if (
        len(possibilities) != len(conditions)
        and len(possibilities) != len(conditions) + 1
    ):
        raise ValueError(
            "The number of possibilities must be equal to the number of conditions or to the number of conditions plus one (to allow for a default possibility)"
        )
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
    Interface to edit an existing node, changing its predecessors.

    Parameters
    ----------
    graph : grapes Graph
        The graph to which to add the step.
    name : hashable (typically string)
        Name of the node to edit.
    recipe : hashable (typically string), optional
        Name of the recipe node to add, if any. Default is None.
    *args : hashables (typically strings)
        Names of nodes to add as positional dependencies.
    **kwargs : hashables (typically strings)
        Names of nodes to add as keyword dependencies. Keys in the dicts are the keywords to be used when calling the recipe.

    Raises
    ------
    KeyError
        If the node does not exist.
    """
    if name not in graph.nodes:
        raise KeyError("Cannot edit non-existent node " + name)

    # Store old attributes
    was_recipe = get_is_recipe(graph, name)
    was_frozen = get_is_frozen(graph, name)
    had_value = get_has_value(graph, name)
    old_value = None
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
    Interface to remove an existing node, without changing anything else.

    Parameters
    ----------
    graph : grapes Graph
        The graph from which to remove the step.
    name : hashable (typically string)
        Name of the node to remove.

    Raises
    ------
    KeyError
        If the node does not exist.
    """
    if name not in graph.nodes:
        raise KeyError("Cannot edit non-existent node " + name)
    graph._nxdg.remove_node(name)


def finalize_definition(graph):
    """
    Perform operations that should typically be done after the definition of a graph is completed.

    Currently, this freezes all values, because it is assumed that values given during definition are to be frozen.
    It also marks dependencies of recipes as recipes themselves.

    Parameters
    ----------
    graph : grapes Graph
        The graph to finalize.
    """
    make_recipe_dependencies_also_recipes(graph)
    compute_topological_generation_indexes(graph)
    freeze(graph)
