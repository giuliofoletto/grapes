"""
This module contains tests of execution performance.
"""

import timeit

import pytest

import grapes as gr


# Define some functions to be used in the graph
def op_c(x, y):
    return x + y


def op_f(x, y):
    return x * y


def op_i(x, y):
    return x**y


def op_j(x, y, z):
    return (x + y + z) / (x * y * z)


def create_graph():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "f", "op_f", "d", "e")
    gr.add_step(g, "i", "op_i", "g", "h")
    gr.add_step(g, "j", "op_j", "c", "f", "i")
    gr.update_internal_context(
        g, {"op_c": op_c, "op_f": op_f, "op_i": op_i, "op_j": op_j}
    )
    gr.finalize_definition(g)
    return g


# Keep the direct execution of the function as benchmark
def function(a, b, d, e, g, h):
    c = op_c(a, b)
    f = op_f(d, e)
    i = op_i(g, h)
    j = op_j(c, f, i)
    return j


BASE_NUMBER_EXECUTIONS = int(3e5)
a, b, d, e, g, h = 1, 2, 3, 4, 5, 6
context = {"a": a, "b": b, "d": d, "e": e, "g": g, "h": h}
acceptance_margin = 1.50  # 50%


def test_full_execution():
    """
    Test the performance of basic execute_graph_from_context against direct function execution.
    """
    # Expected ratio of execution time (graph / direct function)
    expected_ratio = 1000
    accepted_ratio = int(expected_ratio * acceptance_margin)
    graph = create_graph()

    n = BASE_NUMBER_EXECUTIONS
    t_func = timeit.timeit(lambda: function(a, b, d, e, g, h), number=n) / n

    n = BASE_NUMBER_EXECUTIONS // expected_ratio
    t_graph = (
        timeit.timeit(
            lambda: gr.execute_graph_from_context(graph, context, "j"), number=n
        )
        / n
    )

    assert (
        t_graph < accepted_ratio * t_func
    ), f"The ratio between graph and function execution time {t_graph/t_func} exceeds accepted ratio {accepted_ratio}"


def test_inplace_nocheck_execution():
    """
    Test the performance of execute_graph_from_context with inplace = True and check_feasibility = False against direct function execution.
    """
    # Expected ratio of execution time (graph / direct function)
    expected_ratio = 100
    accepted_ratio = int(expected_ratio * acceptance_margin)
    graph = create_graph()

    n = BASE_NUMBER_EXECUTIONS
    t_func = timeit.timeit(lambda: function(a, b, d, e, g, h), number=n) / n

    n = BASE_NUMBER_EXECUTIONS // expected_ratio
    t_graph = (
        timeit.timeit(
            lambda: gr.execute_graph_from_context(
                graph, context, "j", inplace=True, check_feasibility=False
            ),
            number=n,
        )
        / n
    )

    assert (
        t_graph < accepted_ratio * t_func
    ), f"The ratio between graph and function execution time {t_graph/t_func} exceeds accepted ratio {accepted_ratio}"


def test_bare_execution():  # TODO rework because now the execution happens only once
    """
    Test the performance of execute_to_targets with context already set against direct function execution.
    """
    # Expected ratio of execution time (graph / direct function)
    expected_ratio = 100
    accepted_ratio = int(expected_ratio * acceptance_margin)
    graph = create_graph()
    gr.update_internal_context(graph, context)
    gr.freeze(graph)  # To restore the graph to this state

    def run_func():
        gr.execute_to_targets(graph, "j")
        gr.clear_values(graph)  # Restore state of graph

    n = BASE_NUMBER_EXECUTIONS
    t_func = timeit.timeit(lambda: function(a, b, d, e, g, h), number=n) / n

    n = BASE_NUMBER_EXECUTIONS // expected_ratio
    t_graph = timeit.timeit(run_func, number=n) / n

    assert (
        t_graph < accepted_ratio * t_func
    ), f"The ratio between graph and function execution time {t_graph/t_func} exceeds accepted ratio {accepted_ratio}"


def test_wrap_execution():
    """
    Test the performance of wrap_graph_with_function against direct function execution.
    """
    # Expected ratio of execution time (graph / direct function)
    expected_ratio = 100
    accepted_ratio = int(expected_ratio * acceptance_margin)
    graph = create_graph()
    wrap = gr.wrap_graph_with_function(
        graph,
        ["a", "b", "d", "e", "g", "h"],
        "j",
        input_as_kwargs=False,
        output_as_dict=False,
    )

    n = BASE_NUMBER_EXECUTIONS
    t_func = timeit.timeit(lambda: function(a, b, d, e, g, h), number=n) / n

    n = BASE_NUMBER_EXECUTIONS // expected_ratio
    t_graph = timeit.timeit(lambda: wrap(a, b, d, e, g, h), number=n) / n

    assert (
        t_graph < accepted_ratio * t_func
    ), f"The ratio between graph and function execution time {t_graph/t_func} exceeds accepted ratio {accepted_ratio}"


def test_lambdify_execution():
    """
    Test the performance of lambdify_graph against direct function execution.
    """
    # Expected ratio of execution time (graph / direct function)
    expected_ratio = 10
    accepted_ratio = int(expected_ratio * acceptance_margin)
    graph = create_graph()
    lambd = gr.lambdify_graph(graph, ["a", "b", "d", "e", "g", "h"], "j")

    n = BASE_NUMBER_EXECUTIONS
    t_func = timeit.timeit(lambda: function(a, b, d, e, g, h), number=n) / n

    n = BASE_NUMBER_EXECUTIONS // expected_ratio
    t_graph = timeit.timeit(lambda: lambd(a=a, b=b, d=d, e=e, g=g, h=h), number=n) / n

    assert (
        t_graph < accepted_ratio * t_func
    ), f"The ratio between graph and function execution time {t_graph/t_func} exceeds accepted ratio {accepted_ratio}"
