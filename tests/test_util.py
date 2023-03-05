"""
Tests of utilities.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest
import grapes as gr
import warnings


def test_wrap_with_function():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)
    g.finalize_definition()

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(g, ["a", "b", "c", "d"], "g", input_as_kwargs=False)
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(g, ["a", "b", "c", "d"], "e", "f", "g", input_as_kwargs=False)
    assert f1(1, 2, 3, 4) == -9
    assert f2(1, 2, 3, 4) == [3, 12, -9]


def test_lambdify():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)
    g.finalize_definition()

    # Get a function a,b,c,d -> g
    f1 = gr.lambdify_graph(g, ["a", "b", "c", "d"], "g")
    assert f1(a=1, b=2, c=3, d=4) == -9


def test_execution_with_feasibility_check():
    g = gr.Graph()
    g.add_step("b", "fb", "a")
    g["fb"] = lambda a: a
    g.finalize_definition()

    # a is not available
    with pytest.raises(ValueError):
        gr.execute_graph_from_context(g, {}, "b")
    # Now a becomes available
    res = gr.execute_graph_from_context(g, {"a": 1}, "b")
    assert res["b"] == 1


def test_execution_with_feasibility_check_uncertain():
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g.add_step_quick("condition", lambda pre_req: pre_req)
    g["pre_req"] = True
    g["value_true"] = 1
    g.finalize_definition()

    # Reachability is uncertain because condition is reachable and one value also is
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = gr.execute_graph_from_context(g, {}, "name")
        assert len(w) == 1
        # But the computation is actually feasible
        assert res["name"] == 1


def test_unfeasible_wrap():
    g = gr.Graph()
    g.add_step("d", "op_d", "a", "b", "c")
    g["op_d"] = lambda a, b, c: a + b + c
    g.finalize_definition()

    with pytest.raises(ValueError):
        # Pass b as input, c as constant, but do not pass a
        f1 = gr.wrap_graph_with_function(g, ["b"], "d", constants={"c": 1}, input_as_kwargs=False)
    # Pass also a
    f2 = gr.wrap_graph_with_function(g, ["a", "b"], "d", constants={"c": 1}, input_as_kwargs=False)
    assert f2(1, 1) == 3


def test_execution_of_all_graph():
    g = gr.Graph()
    g.add_step("c", "f_c", "a", "b")
    g.add_step("f", "f_f", "d", "e")
    g["f_c"] = lambda a, b: a + b
    g["f_f"] = lambda d, e: d * e
    g.finalize_definition()

    # No target means that everything is a target
    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "d": 3, "e": 4})
    assert res["c"] == 3
    assert res["f"] == 12
