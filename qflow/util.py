"""
Some utilities. Also, a more functional API to the execution of graphs.

Author: Giulio Foletto.
"""
import json
import copy


def execute_graph_from_context(graph, context, *targets, inplace=False):
    """Execute a graph up to a target given a context.

    Parameters
    ----------
    graph : qflow Graph
        Graph of the computation.
    context : dict
        Dictionary of the initial context of the computation (input).
    targets : strings (or keys in the graph)
        Indicator of what to compute (desired output).
    inplace : bool
        Whether to modify graph and context inplace (default: False).

    Returns
    -------
    qflow Graph
        Graph with context updated after computation.
    """

    if not inplace:
        graph = copy.deepcopy(graph)
        context = copy.deepcopy(context)

    graph.set_internal_context(context, keep_operations=True)
    graph.execute_to_targets(*targets)

    return graph


def json_from_graph(graph):
    """Get a JSON string representing the context of a graph.

    Parameters
    ----------
    graph : qflow Graph
        Graph containing the context to convert to JSON.

    Returns
    -------
    str
        JSON string that prettily represents the context of the graph.
    """

    context = graph.get_internal_context(only_data=True)
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
