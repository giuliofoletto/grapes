import json
import copy

def execute_graph_from_context(graph, context, *targets, inplace = False):
    """Execute a graph up to a target given a context

    Parameters
    ----------
    graph : qflow Graph
        Graph of the computation
    context : dict
        Dictionary of the initial state of the computation (input)
    targets : strings (or keys in the graph)
        Indicator of what to compute (desired output)
    inplace : bool
        Whether to modify graph and context inplace (default: False)
    
    Returns
    -------
    graph
        Graph with context updated after computation
    """

    if not inplace:
        graph = copy.deepcopy(graph)
        context = copy.deepcopy(context)

    graph.clear_values(keep_operations = True)
    graph.set_internal_state(context)
    graph.execute_to_targets(*targets)

    return graph

def json_from_graph(graph):
    """Get a JSON string representing the context of a graph

    Parameters
    ----------
    graph : qflow Graph
        Graph containing the context to convert to JSON

    Returns
    -------
    str
        JSON string that prettily represents the context of the graph
    """
    
    context = graph.get_internal_state(only_data=True)
    non_serializable_items = {}
    for key, value in context.items():
        try:
            json.dumps(value)
        except:
            non_serializable_items.update({key: str(value)})
    if len(non_serializable_items) > 0: # We must copy the context, to preserve it, and dump a modified version of it
        res = copy.deepcopy(context)
        res.update(non_serializable_items)
    else:
        res = context
    return json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))

def context_from_json_file(file_name):
    """Load a json file into a dict"""
    with open(file_name, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data