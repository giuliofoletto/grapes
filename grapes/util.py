"""
Some utilities. Also, a more functional API to the execution of graphs.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import json
import copy
import warnings


def execute_graph_from_context(graph, context, *targets, inplace=False, check_feasibility=True):
    """Execute a graph up to a target given a context.

    Parameters
    ----------
    graph : grapes Graph
        Graph of the computation.
    context : dict
        Dictionary of the initial context of the computation (input).
    targets : strings (or keys in the graph)
        Indicator of what to compute (desired output).
    inplace : bool
        Whether to modify graph and context inplace (default: False).
    check_feasibility : bool
        Whether to check the feasibility of the computation, which slows performance (default: True).

    Returns
    -------
    grapes Graph
        Graph with context updated after computation.
    """
    if check_feasibility:
        feasibility, missing_dependencies = check_feasibility_of_execution(graph, context, *targets, inplace=inplace)
        if feasibility == "unreachable":
            raise ValueError("The requested computation is unfeasible because of the following missing dependencies: " + ", ".join(missing_dependencies))
        elif feasibility == "uncertain":
            warnings.warn("The feasibility of the requested computation is uncertain because of the following missing dependencies: " + ", ".join(missing_dependencies))

    if not inplace:
        graph = copy.deepcopy(graph)
        context = copy.deepcopy(context)

    graph.set_internal_context(context)
    graph.execute_to_targets(*targets)

    return graph


def json_from_graph(graph):
    """Get a JSON string representing the context of a graph.

    Parameters
    ----------
    graph : grapes Graph
        Graph containing the context to convert to JSON.

    Returns
    -------
    str
        JSON string that prettily represents the context of the graph.
    """

    context = graph.get_internal_context(exclude_recipes=True)
    non_serializable_items = {}
    for key, value in context.items():
        try:
            json.dumps(value)
        except:
            non_serializable_items.update({key: str(value)})
    if len(non_serializable_items) > 0:  # We must copy the context, to preserve it, and dump a modified version of it
        res = copy.deepcopy(context)
        res.update(non_serializable_items)
    else:
        res = context
    return json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))


def context_from_json_file(file_name):
    """
    Load a json file into a dictionary.

    Parameters
    ----------
    file_name: str
        Path to the json file.

    Returns
    dict
        Content of the file as dictionary.
    """
    with open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def wrap_graph_with_function(graph, input_keys, *targets, constants={}, input_as_kwargs=True):
    # Copy graph so as not to pollute the original
    operational_graph = copy.deepcopy(graph)
    # Pass all constants to the graph
    operational_graph.update_internal_context(constants)
    # Freeze so that the constants are fixed
    operational_graph.freeze()
    # Unfreeze the input.
    # Note that this has precedence over constants (i.e., if a key is both input and constant, it is treated as input)
    if len(input_keys) > 0:
        operational_graph.unfreeze(*input_keys)
        operational_graph.clear_values(*input_keys)
    # Move as much as possible towards targets
    operational_graph.progress_towards_targets(*targets)
    # Check feasibility
    placeholder_value = 0
    context = {key: placeholder_value for key in input_keys}
    feasibility, missing_dependencies = check_feasibility_of_execution(operational_graph, context, *targets)
    if feasibility == "unreachable":
        raise ValueError("The requested computation is unfeasible because of the following missing dependencies: " + ", ".join(missing_dependencies))
    elif feasibility == "uncertain":
        warnings.warn("The feasibility of the requested computation is uncertain because of the following missing dependencies: " + ", ".join(missing_dependencies))

    if input_as_kwargs:
        def specific_function(**kwargs):
            # Use for loop rather than dict comprehension because it is a more basic operation
            for key in input_keys:
                operational_graph[key] = kwargs[key]
            operational_graph.execute_to_targets(*targets)
            list_of_values = operational_graph.get_list_of_values(targets)
            # Clear values so that the function can be called again
            operational_graph.clear_values()
            if len(list_of_values) == 1:
                return list_of_values[0]
            else:
                return list_of_values
    else:
        input_keys = list(input_keys)

        def specific_function(*args):
            # Use for loop rather than dict comprehension because it is a more basic operation
            for i in range(len(input_keys)):
                operational_graph[input_keys[i]] = args[i]
            operational_graph.execute_to_targets(*targets)
            list_of_values = operational_graph.get_list_of_values(targets)
            # Clear values so that the function can be called again
            operational_graph.clear_values()
            if len(list_of_values) == 1:
                return list_of_values[0]
            else:
                return list_of_values
    return specific_function


def lambdify_graph(graph, input_keys, target):
    graph = copy.deepcopy(graph)
    graph.unfreeze()
    if len(input_keys) > 0:
        graph.clear_values(*input_keys)
    graph.progress_towards_targets(target)
    while not set(graph.get_args(target) + tuple(graph.get_kwargs(target).values())).issubset(set(input_keys)):
        graph.simplify_all_dependencies(target, exclude=input_keys)
    return graph[graph.get_recipe(target)]


def check_feasibility_of_execution(graph, context, *targets, inplace=False):
    if not inplace:
        graph = copy.deepcopy(graph)
        context = copy.deepcopy(context)

    graph.clear_reachabilities()
    graph.set_internal_context(context)
    graph.find_reachability_targets(*targets)
    feasibility = graph.get_worst_reachability(*targets)
    missing_dependencies = set()
    if feasibility in {"unreachable", "uncertain"}:
        for node in graph.nodes:
            if graph.get_topological_generation_index(node) == 0 and graph.has_reachability(node) and graph.get_reachability(node) != "reachable":
                missing_dependencies.add(node)
    return feasibility, missing_dependencies
