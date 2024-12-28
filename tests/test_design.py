"""
Tests of design functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design
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
        assert g.get_is_recipe(n)
    assert g.get_args("e") == ("a", "b")
    assert g.get_args("f") == ("c", "d")
    assert g.get_args("g") == ("e", "f")
    assert g.get_recipe("e") == "op_e"
    assert g.get_recipe("f") == "op_f"
    assert g.get_recipe("g") == "op_g"


# Design
def test_add_step_disordered():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "d", "e", "f", "g", "op_e", "op_f", "op_g"}:
        assert n in g.nodes
    for n in {"op_e", "op_f", "op_g"}:
        assert g.get_is_recipe(n)
    assert g.get_args("e") == ("a", "b")
    assert g.get_args("f") == ("c", "d")
    assert g.get_args("g") == ("e", "f")
    assert g.get_recipe("e") == "op_e"
    assert g.get_recipe("f") == "op_f"
    assert g.get_recipe("g") == "op_g"


# Design
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
        assert g.get_is_recipe(n)
    assert g.get_args("c") == ("b",)
    assert g.get_args("b") == ("a",)
    assert g.get_recipe("c") == "op_c"
    assert g.get_recipe("b") == "op_b"


# Design
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
    assert g.get_args("c") == ("a", "b")
    assert g.get_recipe("c") == "example_function_only_positional"
    assert g.get_args("d") == (
        "a",
        "b",
    )
    assert g.get_kwargs("d") == {"c": "c"}
    assert g.get_args("e") == ()

    def example_function_with_varargs(*args):
        return 1

    with pytest.raises(ValueError):
        gr.add_step_quick(g, "g", example_function_with_varargs)
    with pytest.raises(TypeError):
        gr.add_step_quick(g, "h", "a non-function object")


# Design
def test_add_simple_conditional():
    g = gr.Graph()
    gr.add_simple_conditional(g, "d", "c", "a", "b")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "d"}:
        assert n in g.nodes
    assert g.get_type("d") == "conditional"
    assert g.get_conditions("d") == ["c"]
    assert g.get_possibilities("d") == ["a", "b"]


# Design
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
    assert g.get_type("result") == "conditional"
    assert g.get_conditions("result") == ["condition_1", "condition_2", "condition_3"]
    assert g.get_possibilities("result") == ["node_1", "node_2", "node_3"]


# Design
def test_edit_step():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    for n in {"a", "b", "c", "op_b", "op_c"}:
        assert n in g.nodes
    assert g.get_args("c") == ("b",)
    assert g.get_recipe("c") == "op_c"
    assert g.get_args("b") == ("a",)
    assert g.get_recipe("b") == "op_b"

    gr.edit_step(g, "b", "new_op_b", "a", "d")

    assert g.get_args("b") == ("a", "d")
    assert g.get_recipe("b") == "new_op_b"


# Design
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


# Context
def test_set_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert g["op_b"] == operations["op_b"]
    assert g["op_c"] == operations["op_c"]
    assert g["a"] == operations["a"]


# Context
def test_get_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert gr.get_internal_context(g) == operations


def test_update_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)
    assert g["a"] == 5

    new_operations = {"op_b": lambda x: 3 * x, "op_c": lambda x: 4 * x}
    gr.update_internal_context(g, new_operations)

    assert g["a"] == 5  # Unchanged
    assert g["op_b"] == new_operations["op_b"]  # Updated


def test_clear_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5})
    assert g.get_has_value("a")
    assert g["a"] == 5

    gr.clear_values(g)

    assert not g.get_has_value("a")
    assert g.get_has_value("op_b")  # Frozen
    assert g.get_has_value("op_c")


def test_get_list_of_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_list_of_values(g, ["a", "b"]) == [5, 10]


def test_get_dict_of_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_dict_of_values(g, ["a", "b"]) == {"a": 5, "b": 10}


def test_get_kwargs_values():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 2})
    assert gr.get_kwargs_values(g, {"exponent": "b"}) == {"exponent": 2}


def test_freeze():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    assert g.get_is_frozen("op_b")
    assert g.get_is_frozen("op_c")
    gr.update_internal_context(g, {"a": 5})
    assert not g.get_is_frozen("a")
    gr.freeze(g, "a")
    assert g.get_is_frozen("a")


def test_unfreeze():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5})
    gr.freeze(g, "a")
    assert g.get_is_frozen("a")
    gr.unfreeze(g, "a")
    assert not g.get_is_frozen("a")


def test_make_recipe_dependencies_also_recipes():
    g = gr.Graph()
    gr.add_step(g, "a", "op_a", "b")
    gr.add_step(g, "op_a", "build_op_a", "c", "pre_op_a")
    gr.add_step(g, "b", "op_b", "c")
    gr.make_recipe_dependencies_also_recipes(g)

    assert g.get_is_recipe("pre_op_a")
    assert not g.get_is_recipe("c")


def test_finalize_definition():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.add_step(g, "op_b", "build_op_b", "pre_op_b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    assert g.get_is_frozen("op_b") and g.get_is_frozen("op_c")
    assert (
        g.get_is_recipe("op_b")
        and g.get_is_recipe("op_c")
        and g.get_is_recipe("build_op_b")
    )
    assert g.get_node_attribute("pre_op_b", "topological_generation_index") == 0
    assert g.get_node_attribute("build_op_b", "topological_generation_index") == 0
    assert g.get_node_attribute("op_b", "topological_generation_index") == 1
    assert g.get_node_attribute("b", "topological_generation_index") == 2
    assert g.get_node_attribute("c", "topological_generation_index") == 3
    assert g.get_node_attribute("a", "topological_generation_index") == 0
    assert g.get_node_attribute("op_c", "topological_generation_index") == 0


# Design
def test_topological_generations():
    g = gr.Graph()
    gr.add_step(g, "d", "fd", "b", "c")
    gr.add_step(g, "b", "fb", "a")
    gr.finalize_definition(g)

    assert g.get_node_attribute("a", "topological_generation_index") == 0
    assert g.get_node_attribute("b", "topological_generation_index") == 1
    assert g.get_node_attribute("c", "topological_generation_index") == 0
    assert g.get_node_attribute("d", "topological_generation_index") == 2
    assert g.get_node_attribute("fb", "topological_generation_index") == 0
    assert g.get_node_attribute("fd", "topological_generation_index") == 0


# Design, features
def test_sources_and_sinks():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "e", "op_e", "d")
    gr.add_step(g, "op_c", "b_op_c", "d_op_c")
    gr.finalize_definition(g)

    assert gr.get_all_sources(g, exclude_recipes=True) == {"a", "b", "d"}
    assert gr.get_all_sources(g, exclude_recipes=False) == {
        "a",
        "b",
        "d",
        "b_op_c",
        "d_op_c",
        "op_e",
    }
    assert gr.get_all_sinks(g, exclude_recipes=True) == {"c", "e"}
    assert gr.get_all_sinks(g, exclude_recipes=False) == {"c", "e"}


# Design, features
def test_get_all_conditionals():
    """
    Get set of all conditionals in the graph.
    """
    g = gr.Graph()
    gr.add_simple_conditional(g, "conditional1", "c1", "vt", "vf")
    gr.add_simple_conditional(g, "conditional2", "c2", "vt", "vf")
    gr.finalize_definition(g)

    assert gr.get_all_conditionals(g) == {"conditional1", "conditional2"}


# Design, features
def test_get_all_ancestors():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.add_step(g, "h", "op_h", "e")
    gr.add_simple_conditional(g, "j", "i", "g", "h")
    gr.finalize_definition(g)

    result_g = gr.get_all_ancestors_target(g, "g")
    result_h = gr.get_all_ancestors_target(g, "h")
    result_j = gr.get_all_ancestors_target(g, "j")

    assert result_g == {"op_g", "e", "f", "op_f", "c", "d", "op_e", "a", "b"}
    assert result_h == {"op_h", "e", "op_e", "a", "b"}
    assert result_j == {
        "i",
        "h",
        "op_h",
        "g",
        "op_g",
        "e",
        "f",
        "op_f",
        "c",
        "d",
        "op_e",
        "a",
        "b",
    }


# Design
def test_make_recipe_dependencies_also_recipes():
    g = gr.Graph()
    gr.add_step(g, "a", "op_a", "b")
    gr.add_step(
        g, "op_a", "build_op_a", "c", "d"
    )  # c and d will be converted to recipes
    gr.add_step(g, "b", "op_b", "c")  # c will no longer be converted to recipe
    gr.finalize_definition(g)  # calls make_recipe_dependencies_also_recipes

    assert g.get_is_recipe("d")
    assert not g.get_is_recipe("c")
