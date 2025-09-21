import grapes as gr

g = gr.Graph()
gr.add_step(g, "b", "compute_b", "a")
gr.add_step(g, "c", "compute_c", "b")
gr.update_internal_context(
    g, {"compute_b": lambda a: 2 * a, "compute_c": lambda b: b + 1}
)
gr.finalize_definition(g)

context = {"a": 3}
target = "c"
result = gr.execute_graph_from_context(g, context, target)
print(result["c"])  # 7
