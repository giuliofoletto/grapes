"""
Tests of design functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


def test_add_step():
    g = gr.Graph()
    gr.add_step(g, "a")
    gr.add_step(g, "b")
    gr.add_step(g, "c")
    gr.add_step(g, "d")
    gr.add_step(g, "op_e")
    gr.add_step(g, "op_f")
    gr.add_step(g, "op_g")
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "d", "e", "f", "g", "op_e", "op_f", "op_g"}:
        assert n in g.nodes
    for n in {"op_e", "op_f", "op_g"}:
        assert gr.get_is_recipe(g, n)
    assert gr.get_args(g, "e") == ("a", "b")
    assert gr.get_args(g, "f") == ("c", "d")
    assert gr.get_args(g, "g") == ("e", "f")
    assert gr.get_recipe(g, "e") == "op_e"
    assert gr.get_recipe(g, "f") == "op_f"
    assert gr.get_recipe(g, "g") == "op_g"


def test_add_step_disordered():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "d", "e", "f", "g", "op_e", "op_f", "op_g"}:
        assert n in g.nodes
    for n in {"op_e", "op_f", "op_g"}:
        assert gr.get_is_recipe(g, n)
    assert gr.get_args(g, "e") == ("a", "b")
    assert gr.get_args(g, "f") == ("c", "d")
    assert gr.get_args(g, "g") == ("e", "f")
    assert gr.get_recipe(g, "e") == "op_e"
    assert gr.get_recipe(g, "f") == "op_f"
    assert gr.get_recipe(g, "g") == "op_g"


def test_add_step_inverted():
    # Typically, we proceed from bottom to top
    # Here we test the opposite
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "b")
    gr.add_step(g, "b", "op_b", "a")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "op_b", "op_c"}:
        assert n in g.nodes
    for n in {"op_b", "op_c"}:
        assert gr.get_is_recipe(g, n)
    assert gr.get_args(g, "c") == ("b",)
    assert gr.get_args(g, "b") == ("a",)
    assert gr.get_recipe(g, "c") == "op_c"
    assert gr.get_recipe(g, "b") == "op_b"


def test_add_step_quick():
    def example_function_only_positional(a, b):
        return a**b

    def example_function_with_kw_only_args(a, b, *, c):
        return a**b + c

    def example_function_with_no_args():
        return 1

    g = gr.Graph()
    gr.add_step_quick(g, "c", example_function_only_positional)
    gr.add_step_quick(g, "d", example_function_with_kw_only_args)
    gr.add_step_quick(g, "e", example_function_with_no_args)
    gr.add_step_quick(g, "f", lambda e: 2 * e)
    gr.finalize_definition(g)

    for n in {"c", "d", "e", "f"}:
        assert n in g.nodes
    assert gr.get_args(g, "c") == ("a", "b")
    assert gr.get_recipe(g, "c") == "example_function_only_positional"
    assert gr.get_args(g, "d") == (
        "a",
        "b",
    )
    assert gr.get_kwargs(g, "d") == {"c": "c"}
    assert gr.get_args(g, "e") == ()

    def example_function_with_varargs(*args):
        return 1

    with pytest.raises(ValueError):
        gr.add_step_quick(g, "g", example_function_with_varargs)
    with pytest.raises(TypeError):
        gr.add_step_quick(g, "h", "a non-function object")


def test_add_simple_conditional():
    g = gr.Graph()
    gr.add_simple_conditional(g, "d", "c", "a", "b")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "d"}:
        assert n in g.nodes
    assert gr.get_type(g, "d") == "conditional"
    assert gr.get_conditions(g, "d") == ["c"]
    assert gr.get_possibilities(g, "d") == ["a", "b"]


def test_add_multiple_conditional():
    g = gr.Graph()
    gr.add_multiple_conditional(
        g,
        "result",
        ["condition_1", "condition_2", "condition_3"],
        ["node_1", "node_2", "node_3"],
    )
    gr.finalize_definition(g)

    for n in {
        "result",
        "condition_1",
        "condition_2",
        "condition_3",
        "node_1",
        "node_2",
        "node_3",
    }:
        assert n in g.nodes
    assert gr.get_type(g, "result") == "conditional"
    assert gr.get_conditions(g, "result") == [
        "condition_1",
        "condition_2",
        "condition_3",
    ]
    assert gr.get_possibilities(g, "result") == ["node_1", "node_2", "node_3"]


def test_edit_step():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "op_b", "op_c"}:
        assert n in g.nodes
    assert gr.get_args(g, "c") == ("b",)
    assert gr.get_recipe(g, "c") == "op_c"
    assert gr.get_args(g, "b") == ("a",)
    assert gr.get_recipe(g, "b") == "op_b"

    gr.edit_step(g, "b", "new_op_b", "a", "d")

    assert gr.get_args(g, "b") == ("a", "d")
    assert gr.get_recipe(g, "b") == "new_op_b"


def test_remove_step():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    gr.remove_step(g, "b")
    with pytest.raises(KeyError):
        g["b"]
    with pytest.raises(ValueError):
        gr.remove_step(g, "d")


def test_finalize_definition():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.add_step(g, "op_b", "build_op_b", "pre_op_b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    assert gr.get_is_frozen(g, "op_b") and gr.get_is_frozen(g, "op_c")
    assert (
        gr.get_is_recipe(g, "op_b")
        and gr.get_is_recipe(g, "op_c")
        and gr.get_is_recipe(g, "build_op_b")
    )
    assert gr.get_topological_generation_index(g, "pre_op_b") == 0
    assert gr.get_topological_generation_index(g, "build_op_b") == 0
    assert gr.get_topological_generation_index(g, "op_b") == 1
    assert gr.get_topological_generation_index(g, "b") == 2
    assert gr.get_topological_generation_index(g, "c") == 3
    assert gr.get_topological_generation_index(g, "a") == 0
    assert gr.get_topological_generation_index(g, "op_c") == 0
