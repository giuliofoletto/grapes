"""
Tests of features functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Features
def test_freeze():
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


# Features
def test_unfreeze():
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


# Features
def test_topological_generations():
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


# Features
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


# Features
def test_get_all_conditionals():
    """
    Get set of all conditionals in the graph.
    """
    g = gr.Graph()
    gr.add_simple_conditional(g, "conditional1", "c1", "vt", "vf")
    gr.add_simple_conditional(g, "conditional2", "c2", "vt", "vf")
    gr.finalize_definition(g)

    assert gr.get_all_conditionals(g) == {"conditional1", "conditional2"}


# Features
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


# Features
def test_make_recipe_dependencies_also_recipes():
    g = gr.Graph()
    gr.add_step(g, "a", "op_a", "b")
    gr.add_step(
        g, "op_a", "build_op_a", "c", "d"
    )  # c and d will be converted to recipes
    gr.add_step(g, "b", "op_b", "c")  # c will no longer be converted to recipe
    gr.finalize_definition(g)  # calls make_recipe_dependencies_also_recipes

    assert gr.get_is_recipe(g, "d")
    assert not gr.get_is_recipe(g, "c")
