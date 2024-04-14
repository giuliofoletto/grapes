"""
Tests of simplification functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, context, simplify, evaluate
def test_simplify_dependency():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    gr.simplify_dependency(g, "g", "f")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    gr.execute_to_targets(g, "g")

    assert g["g"] == -9


# Design, context, simplify, evaluate
def test_simplify_all_dependencies():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    gr.simplify_all_dependencies(g, "g")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    gr.execute_to_targets(g, "g")

    assert g["g"] == -9


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step():
    """
    Convert conditional to a trivial step since its condition c2 already has true value.
    """
    g = gr.Graph()
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["c2"] = True
    g["v2"] = 2
    g.finalize_definition()

    gr.convert_conditional_to_trivial_step(g, "conditional")
    assert g.get_type("conditional") == "standard"

    gr.execute_to_targets(g, "conditional")
    assert g["conditional"] == g["v2"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_with_evaluation():
    """
    Convert conditional to a trivial step but compute the conditions.
    """
    g = gr.Graph()
    g.add_step("v2", "identity_recipe", "pre_v2")
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = True
    g["pre_v2"] = 2
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    gr.convert_conditional_to_trivial_step(
        g, "conditional", execute_towards_conditions=True
    )
    assert g.get_type("conditional") == "standard"

    gr.execute_to_targets(g, "conditional")
    assert g["conditional"] == g["v2"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_with_default():
    """
    Convert conditional to a trivial step, computing conditions, but use default value since no condition is true.
    """
    g = gr.Graph()
    g.add_step("default", "identity_recipe", "pre_default")
    g.add_step("c", "identity_recipe", "pre_c")
    g.add_multiple_conditional("conditional", ["c"], ["v", "default"])
    g["pre_c"] = False
    g["pre_default"] = 1
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    gr.convert_conditional_to_trivial_step(
        g, "conditional", execute_towards_conditions=True
    )
    assert g.get_type("conditional") == "standard"

    gr.execute_to_targets(g, "conditional")
    assert g["conditional"] == g["default"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_without_true_values():
    """
    Try to convert conditional to trivial step but no conditions can be evaluated to true.
    """
    g = gr.Graph()
    g.add_step("v2", "identity_recipe", "pre_v2")
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = False
    g["pre_v2"] = 2
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    with pytest.raises(ValueError):
        gr.convert_conditional_to_trivial_step(
            g, "conditional", execute_towards_conditions=True
        )


# Design, simplify, evaluate
def test_convert_all_conditionals_to_trivial_steps():
    """
    Convert all conditionals to trivial steps.
    """
    g = gr.Graph()
    g.add_simple_conditional("conditional1", "c1", "vt", "vf")
    g.add_simple_conditional("conditional2", "c2", "vt", "vf")
    g["c1"] = True
    g["c2"] = False
    g["vt"] = 1
    g["vf"] = 2
    g.finalize_definition()

    gr.convert_all_conditionals_to_trivial_steps(g)
    assert g.get_type("conditional1") == "standard"
    assert g.get_type("conditional2") == "standard"

    gr.execute_to_targets(g, "conditional1", "conditional2")
    assert g["conditional1"] == g["vt"]
    assert g["conditional2"] == g["vf"]


# Design, simplify, evaluate
def test_convert_all_conditionals_to_trivial_steps_with_evaluation():
    """
    Convert all conditionals to trivial steps, computing the conditions.
    """
    g = gr.Graph()
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g.add_step("c1", "op_id", "pre_c1")
    g.add_step("c2", "op_id", "pre_c2")
    g.add_step("c3", "op_id", "pre_c3")
    g["pre_c1"] = True
    g["pre_c2"] = False
    g["pre_c3"] = False
    g["op_id"] = lambda x: x
    g["v1"] = 1
    g["v2"] = 2
    g["v3"] = 3
    g.finalize_definition()

    gr.convert_all_conditionals_to_trivial_steps(g, execute_towards_conditions=True)
    assert g.get_type("conditional") == "standard"

    gr.execute_to_targets(g, "conditional")
    assert g["conditional"] == g["v1"]
