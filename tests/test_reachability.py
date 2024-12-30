"""
Tests of reachability functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, context, reachability
def test_reachability_simple():
    g = gr.Graph()
    gr.add_step(g, "b", "fb", "a")
    g["fb"] = lambda a: a
    gr.finalize_definition(g)

    gr.find_reachability_targets(g, "b")
    assert gr.get_reachability(g, "b") == "unreachable"
    gr.clear_reachabilities(g)

    gr.update_internal_context(g, {"a": 1})
    gr.find_reachability_targets(g, "b")
    assert gr.get_reachability(g, "b") == "reachable"


# Design, context, reachability
def test_reachability_long_graph():
    g = gr.Graph()
    gr.add_step_quick(g, "c", lambda b: b)
    gr.add_step_quick(g, "b", lambda a: a)
    gr.finalize_definition(g)

    gr.find_reachability_targets(g, "b")
    assert gr.get_reachability(g, "b") == "unreachable"
    gr.clear_reachabilities(g)

    gr.update_internal_context(g, {"a": 1})
    gr.find_reachability_targets(g, "b")
    assert gr.get_reachability(g, "b") == "reachable"


# Design, context, reachability
def test_reachability_conditional_with_true_value():
    g = gr.Graph()
    gr.add_simple_conditional(g, "name", "condition", "value_true", "value_false")
    g["condition"] = True
    gr.finalize_definition(g)

    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    gr.update_internal_context(g, {"value_true": 1})
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "reachable"


# Design, context, reachability
def test_reachability_multiple_conditional_with_true_value():
    g = gr.Graph()
    gr.add_multiple_conditional(g, "name", ["ca", "cb"], ["a", "b", "c"])
    g["ca"] = True
    gr.finalize_definition(g)

    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    gr.update_internal_context(g, {"a": 1})
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "reachable"


# Design, context, reachability
def test_conditional_no_conditions_defined():
    g = gr.Graph()
    gr.add_simple_conditional(g, "name", "condition", "value_true", "value_false")
    gr.add_step_quick(g, "condition", lambda pre_req: pre_req)
    gr.finalize_definition(g)

    # Here, condition and possibilities are unreachable
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    # Here, condition is undefined but reachable, but all values are unreachable
    g["pre_req"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["value_true"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["value_false"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "reachable"


# Design, context, reachability
def test_multiple_conditional_no_conditions_defined():
    g = gr.Graph()
    gr.add_multiple_conditional(g, "name", ["ca", "cb"], ["va", "vb", "vc"])
    gr.add_step_quick(g, "ca", lambda pa: pa)
    gr.add_step_quick(g, "cb", lambda pb: pb)
    gr.finalize_definition(g)

    # Here, condition and possibilities are unreachable
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    # Here, ca is undefined but reachable, but all values are unreachable
    g["pa"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "unreachable"
    gr.clear_reachabilities(g)

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["va"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are reachable, but the conditional is still uncertain because we do not know which condition is True
    g["pb"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["vb"] = 1
    g["vc"] = 1
    gr.find_reachability_targets(g, "name")
    assert gr.get_reachability(g, "name") == "reachable"
