"""
Tests of merge functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, merge
def test_compatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    assert gr.check_compatibility(g, h)


# Design, merge
def test_incompatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("c", "op_c2", "a", "d")
    assert not gr.check_compatibility(g, h)


# Design, merge
def test_merge():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")

    res = gr.merge(g, h)
    assert res == exp


# Design, merge, context, evaluate
def test_merge_and_execute():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    g = gr.merge(g, h)
    g.finalize_definition()

    g.update_internal_context(
        {"a": 1, "b": 2, "d": 4, "op_c": lambda x, y: x + y, "op_e": lambda x, y: x * y}
    )
    gr.execute_to_targets(g, "e")

    assert g["e"] == 12


# Design, context, util, evaluate
def test_get_subgraph():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()

    h = gr.get_subgraph(g, {"g", "e", "f", "op_g"})
    h.set_internal_context({"e": 1, "f": 2, "op_g": lambda x, y: x + y})
    gr.execute_to_targets(h, "g")
    assert h["g"] == 3
