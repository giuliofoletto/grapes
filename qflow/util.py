def execute_graph_from_context(graph, context, targets = []):
    graph.clear_values()
    graph.set_internal_state(context)
    graph.execute_to_targets(targets)
    return graph.get_internal_state()