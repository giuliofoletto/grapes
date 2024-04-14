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
    g.add_step("b", "fb", "a")
    g["fb"] = lambda a: a
    g.finalize_definition()

    gr.find_reachability_targets(g, "b")
    assert g.get_reachability("b") == "unreachable"
    gr.clear_reachabilities(g)

    g.update_internal_context({"a": 1})
    gr.find_reachability_targets(g, "b")
    assert g.get_reachability("b") == "reachable"


# Design, context, reachability
def test_reachability_long_graph():
    g = gr.Graph()
    g.add_step_quick("c", lambda b: b)
    g.add_step_quick("b", lambda a: a)
    g.finalize_definition()

    gr.find_reachability_targets(g, "b")
    assert g.get_reachability("b") == "unreachable"
    gr.clear_reachabilities(g)

    g.update_internal_context({"a": 1})
    gr.find_reachability_targets(g, "b")
    assert g.get_reachability("b") == "reachable"


# Design, context, reachability
def test_reachability_conditional_with_true_value():
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g["condition"] = True
    g.finalize_definition()

    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    g.update_internal_context({"value_true": 1})
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "reachable"


# Design, context, reachability
def test_reachability_multiple_conditional_with_true_value():
    g = gr.Graph()
    g.add_multiple_conditional("name", ["ca", "cb"], ["a", "b", "c"])
    g["ca"] = True
    g.finalize_definition()

    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    g.update_internal_context({"a": 1})
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "reachable"


# Design, context, reachability
def test_conditional_no_conditions_defined():
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g.add_step_quick("condition", lambda pre_req: pre_req)
    g.finalize_definition()

    # Here, condition and possibilities are unreachable
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    # Here, condition is undefined but reachable, but all values are unreachable
    g["pre_req"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["value_true"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["value_false"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "reachable"


# Design, context, reachability
def test_multiple_conditional_no_conditions_defined():
    g = gr.Graph()
    g.add_multiple_conditional("name", ["ca", "cb"], ["va", "vb", "vc"])
    g.add_step_quick("ca", lambda pa: pa)
    g.add_step_quick("cb", lambda pb: pb)
    g.finalize_definition()

    # Here, condition and possibilities are unreachable
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    # Here, ca is undefined but reachable, but all values are unreachable
    g["pa"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "unreachable"
    gr.clear_reachabilities(g)

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["va"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are reachable, but the conditional is still uncertain because we do not know which condition is True
    g["pb"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "uncertain"
    gr.clear_reachabilities(g)

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["vb"] = 1
    g["vc"] = 1
    gr.find_reachability_targets(g, "name")
    assert g.get_reachability("name") == "reachable"
