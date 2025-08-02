"""
Tests of evaluation functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


def test_execute_to_targets():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")

    def example_exponentiation_func(base, exponent):
        return base**exponent

    gr.update_internal_context(g, {"a": 5, "b": 2, "op_c": example_exponentiation_func})
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "c")

    assert g["c"] == 25


def test_execute_to_targets_with_conditional():
    g = gr.Graph()
    gr.add_step(g, "c1", "identity_recipe", "pre_c1")
    gr.add_step(g, "c2", "identity_recipe", "pre_c2")
    gr.add_step(g, "c3", "identity_recipe", "pre_c3")
    gr.add_multiple_conditional(
        g, "conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"]
    )
    g["pre_c1"] = False
    g["pre_c2"] = True
    g["pre_c3"] = False
    g["identity_recipe"] = lambda x: x
    g["v1"] = 1
    g["v2"] = 2
    g["v3"] = 3
    gr.finalize_definition(g)

    gr.execute_to_targets(g, "conditional")

    assert g["c1"] == False
    assert g["c2"] == True
    assert not gr.get_has_value(
        g, "c3"
    )  # c3 is not computed because c2 is found to be True
    assert g["conditional"] == g["v2"]


def test_execute_to_targets_with_kwargs():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")
    gr.finalize_definition(g)

    def example_exponentiation_func(base, exponent):
        return base**exponent

    gr.update_internal_context(g, {"a": 5, "b": 2, "op_c": example_exponentiation_func})
    gr.execute_to_targets(g, "c")

    assert g["c"] == 25


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

    assert not gr.get_has_value(g, "c1")
    assert not gr.get_has_value(g, "c3")
    assert g["c2"] == True


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

    assert not gr.get_has_value(g, "c1")
    assert not gr.get_has_value(g, "c3")
    assert g["c2"] == True
