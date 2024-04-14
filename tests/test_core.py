"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, context, evaluate
def test_simple():
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

    gr.update_internal_context(
        g,
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        },
    )
    gr.execute_to_targets(g, "g")

    assert g["g"] == -9


# Design, context, evaluate
def test_simplified_input():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    gr.update_internal_context(
        g,
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        },
    )
    gr.execute_to_targets(g, "g")

    assert g["g"] == -9


# Design, context, evaluate
def test_diamond():
    g = gr.Graph()
    gr.add_step(g, "a")
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.add_step(g, "d", "op_d", "b")
    gr.add_step(g, "e", "op_e", "c", "d")
    gr.finalize_definition(g)

    gr.update_internal_context(
        g,
        {
            "a": 1,
            "op_b": lambda x: 2 * x,
            "op_c": lambda x: 2 * x,
            "op_d": lambda x: 2 * x,
            "op_e": lambda x, y: x - y,
        },
    )
    gr.execute_to_targets(g, "e")

    assert g["e"] == 0


# Design, context, evaluate
def test_inverted_input():
    # Typically, we proceed from bottom to top
    # Here we test the opposite
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "b")
    gr.add_step(g, "b", "op_b", "a")
    gr.finalize_definition(g)

    gr.update_internal_context(
        g, {"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    )
    gr.execute_to_targets(g, "c")

    assert g["c"] == 6


# Design, context, evaluate
def test_conditional():
    g = gr.Graph()
    gr.add_simple_conditional(g, "d", "c", "a", "b")
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 1, "b": 2, "c": True})
    gr.execute_to_targets(g, "d")

    assert g["d"] == g["a"]


# Design, context, evaluate
def test_kwargs():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")
    gr.finalize_definition(g)

    def example_exponentiation_func(base, exponent):
        return base**exponent

    gr.update_internal_context(g, {"a": 5, "b": 2, "op_c": example_exponentiation_func})
    gr.execute_to_targets(g, "c")

    assert g["c"] == 25


# Design, context, evaluate
def test_progress_towards_targets():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "f", "op_f", "b", "c", "e")
    gr.add_step(g, "e", "op_e", "d")

    context = {
        "op_b": lambda x: 2 * x,
        "op_e": lambda x: 3 * x,
        "op_f": lambda x, y, z: x + y + z,
        "a": 5,
        "d": 4,
    }
    gr.set_internal_context(g, context)
    gr.finalize_definition(g)

    # f cannot be reached because c is not in context, but b and e can be computed
    gr.progress_towards_targets(g, "f")
    assert g["b"] == 10
    assert g["e"] == 12


# Design, context, evaluate
def test_multiple_conditional():
    g = gr.Graph()
    gr.add_multiple_conditional(
        g,
        "result",
        ["condition_1", "condition_2", "condition_3"],
        ["node_1", "node_2", "node_3"],
    )
    context = {
        "condition_1": False,
        "condition_2": True,
        "condition_3": False,
        "node_1": 1,
        "node_2": 2,
        "node_3": 3,
    }
    gr.set_internal_context(g, context)
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "result")

    assert g["result"] == 2


# Design, context, evaluate
def test_multiple_conditional_with_default():
    g = gr.Graph()
    gr.add_multiple_conditional(
        g,
        "result",
        ["condition_1", "condition_2", "condition_3"],
        ["node_1", "node_2", "node_3", "node_default"],
    )
    context = {
        "condition_1": False,
        "condition_2": False,
        "condition_3": False,
        "node_1": 1,
        "node_2": 2,
        "node_3": 3,
        "node_default": 4,
    }
    gr.set_internal_context(g, context)
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "result")

    assert g["result"] == 4


# Design, context, evaluate
def test_edit_step():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.set_internal_context(
        g, {"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    )
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "c")
    assert g["b"] == 2
    assert g["c"] == 6

    gr.edit_step(g, "b", "new_op_b", "a", "d")
    assert g["b"] == 2  # Value is unchanged
    assert g["c"] == 6  # Value is unchanged

    gr.clear_values(g, "b", "c")
    gr.update_internal_context(g, {"d": 3, "new_op_b": lambda x, y: x + y})
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "c")
    assert g["b"] == 4
    assert g["c"] == 12


# Design, context, evaluate
def test_remove_step():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.set_internal_context(
        g, {"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    )
    gr.finalize_definition(g)

    gr.remove_step(g, "b")
    with pytest.raises(KeyError):
        g["b"]
    with pytest.raises(ValueError):
        gr.remove_step(g, "d")


# Design, context, evaluate
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
    gr.update_internal_context(g, {"a": 2, "b": 3})
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "d", "f")  # "c" and "e" should be automatically computed
    assert g["c"] == 8
    assert g["d"] == 16
    assert g["e"] == 1
    assert g["f"] == 2

    def example_function_with_varargs(*args):
        return 1

    with pytest.raises(ValueError):
        gr.add_step_quick(g, "g", example_function_with_varargs)
    with pytest.raises(TypeError):
        gr.add_step_quick(g, "h", "a non-function object")


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


# Design, evaluate
def test_execute_towards_conditions():
    """
    Execute towards the conditions of conditional by computing c2.
    """
    g = gr.Graph()
    gr.add_step(g, "c2", "identity_recipe", "pre_c2")
    gr.add_multiple_conditional(
        g, "conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"]
    )
    g["pre_c2"] = True
    g["identity_recipe"] = lambda x: x
    gr.finalize_definition(g)

    gr.execute_towards_conditions(g, "c1", "c2", "c3")

    assert not g.get_has_value("c1")
    assert not g.get_has_value("c3")
    assert g["c2"] == True


# Design, evaluate
def test_execute_towards_all_conditions_of_conditional():
    """
    Execute towards the conditions of conditional by computing c2 (the conditional is passed instead of the conditions).
    """
    g = gr.Graph()
    gr.add_step(g, "c2", "identity_recipe", "pre_c2")
    gr.add_multiple_conditional(
        g, "conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"]
    )
    g["pre_c2"] = True
    g["identity_recipe"] = lambda x: x
    gr.finalize_definition(g)

    gr.execute_towards_all_conditions_of_conditional(g, "conditional")

    assert not g.get_has_value("c1")
    assert not g.get_has_value("c3")
    assert g["c2"] == True


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
