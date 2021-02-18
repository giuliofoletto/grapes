def execute_graph_from_context(graph, context, *targets):
    """Execute a graph up to a target given a context

    Parameters
    ----------
    graph : qflow Graph
        Graph of the computation
    context : dict
        Dictionary of the initial state of the computation (input)
    targets : strings (or keys in the graph)
        Indicator of what to compute (desired output)
    
    Returns
    -------
    dict
        Final state of the computation (context is not modified in place, a deep copy is used)
    """

    graph.clear_values(keep_operations = True)
    graph.set_internal_state(context)
    graph.execute_to_targets(*targets)
    final_context = graph.get_internal_state(only_data = True)

    return final_context