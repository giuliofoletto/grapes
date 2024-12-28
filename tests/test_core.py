"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


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
