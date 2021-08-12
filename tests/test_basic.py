"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest
import grapes as gr


def test_simple():
    g = gr.Graph()
    g.add_step("a")
    g.add_step("b")
    g.add_step("c")
    g.add_step("d")
    g.add_step("op_e")
    g.add_step("op_f")
    g.add_step("op_g")
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}, "g")
    assert res["g"] == -9


def test_simplified_input():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}, "g")
    assert res["g"] == -9


def test_diamond():
    g = gr.Graph()
    g.add_step("a")
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.add_step("d", "op_d", "b")
    g.add_step("e", "op_e", "c", "d")

    res = gr.execute_graph_from_context(g, {"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 2*x, "op_d": lambda x: 2*x, "op_e": lambda x, y: x-y}, "e")
    assert res["e"] == 0


def test_conditional():
    g = gr.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "c": True}, "d")
    assert res["d"] == res["a"]


def test_compatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    assert h.is_compatible(g)


def test_incompatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("c", "op_c2", "a", "d")
    assert not h.is_compatible(g)


def test_merge():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    g.merge(h)

    assert g == exp


def test_merge_and_execute():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    g.merge(h)

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "d": 4, "op_c": lambda x, y: x+y, "op_e": lambda x, y: x*y}, "e")
    assert res["e"] == 12


def test_kwargs():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", exponent="b")

    def example_exponentiation_func(base, exponent):
        return base**exponent
    res = gr.execute_graph_from_context(g, {"a": 5, "b": 2, "op_c": example_exponentiation_func}, "c")
    assert res["c"] == 25


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


def test_simplify_dependency():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    g.simplify_dependency("g", "f")
    g.finalize_definition()

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "c": 3, "d": 4}, "g")
    assert res["g"] == -9


def test_simplify_all_dependencies():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    g.simplify_all_dependencies("g")
    g.finalize_definition()

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "c": 3, "d": 4}, "g")
    assert res["g"] == -9
