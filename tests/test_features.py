"""
This module contains tests of features functionality.
"""

import pytest

import grapes as gr


def test_freeze():
    """
    Test freezing nodes in a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    assert gr.get_is_frozen(g, "op_b")
    assert gr.get_is_frozen(g, "op_c")
    gr.update_internal_context(g, {"a": 5})
    assert not gr.get_is_frozen(g, "a")
    gr.freeze(g, "a")
    assert gr.get_is_frozen(g, "a")


def test_unfreeze():
    """
    Test unfreezing nodes in a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5})
    gr.freeze(g, "a")
    assert gr.get_is_frozen(g, "a")
    gr.unfreeze(g, "a")
    assert not gr.get_is_frozen(g, "a")


def test_get_topological_generation_index():
    """
    Test getting the topological generation index of nodes in a graph (without computing it).
    """
    g = gr.Graph()
    gr.add_step(g, "d", "fd", "b", "c")
    gr.add_step(g, "b", "fb", "a")
    gr.finalize_definition(g)

    assert gr.get_topological_generation_index(g, "a") == 0
    assert gr.get_topological_generation_index(g, "b") == 1
    assert gr.get_topological_generation_index(g, "c") == 0
    assert gr.get_topological_generation_index(g, "d") == 2
    assert gr.get_topological_generation_index(g, "fb") == 0
    assert gr.get_topological_generation_index(g, "fd") == 0


def test_get_all_nodes():
    """
    Test getting set of all nodes in the graph, optionally excluding recipes.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "e", "op_e", "d")
    gr.add_step(g, "op_c", "b_op_c", "d_op_c")
    gr.finalize_definition(g)

    assert gr.get_all_nodes(g, exclude_recipes=True) == {"a", "b", "c", "d", "e"}
    assert gr.get_all_nodes(g, exclude_recipes=False) == {
        "a",
        "b",
        "c",
        "d",
        "e",
        "op_c",
        "op_e",
        "b_op_c",
        "d_op_c",
    }


def test_get_all_sources():
    """
    Test getting set of all source nodes in the graph, optionally excluding recipes.
    """
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


def test_get_all_sinks():
    """
    Test getting set of all sink nodes in the graph, optionally excluding recipes.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "e", "op_e", "d")
    gr.add_step(g, "op_c", "b_op_c", "d_op_c")
    gr.finalize_definition(g)

    assert gr.get_all_sinks(g, exclude_recipes=True) == {"c", "e"}
    assert gr.get_all_sinks(g, exclude_recipes=False) == {"c", "e"}


def test_get_all_conditionals():
    """
    Test getting set of all conditionals in the graph.
    """
    g = gr.Graph()
    gr.add_simple_conditional(g, "conditional1", "c1", "vt", "vf")
    gr.add_simple_conditional(g, "conditional2", "c2", "vt", "vf")
    gr.finalize_definition(g)

    assert gr.get_all_conditionals(g) == {"conditional1", "conditional2"}


def test_get_all_ancestors_target():
    """
    Test getting all ancestors of a target node in the graph.
    """
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


def test_make_recipe_dependencies_also_recipes():
    """
    Test making recipe dependencies also recipes in a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "a", "op_a", "b")
    gr.add_step(
        g, "op_a", "build_op_a", "c", "d"
    )  # c and d will be converted to recipes
    gr.add_step(g, "b", "op_b", "c")  # c will no longer be converted to recipe
    gr.make_recipe_dependencies_also_recipes(g)
    gr.finalize_definition(
        g
    )  # make_recipe_dependencies_also_recipes is also called here

    assert gr.get_is_recipe(g, "d")
    assert not gr.get_is_recipe(g, "c")


def test_get_all_recipes():
    """
    Test getting set of all recipes in the graph, including those converted when calling finalize_definition.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "e", "op_e", "d")
    gr.add_step(g, "op_c", "b_op_c", "d_op_c")
    assert gr.get_all_recipes(g) == set(["op_c", "op_e", "b_op_c"])
    gr.finalize_definition(g)  # Calls make_recipe_dependencies_also_recipes
    assert gr.get_all_recipes(g) == set(["op_c", "op_e", "b_op_c", "d_op_c"])
