"""
Tests of merge functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


def test_check_compatibility():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    h = gr.Graph()
    gr.add_step(h, "e", "op_e", "c", "d")
    assert gr.check_compatibility(g, h)


def test_check_compatibility_incompatible():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    h = gr.Graph()
    gr.add_step(h, "c", "op_c2", "a", "d")
    assert not gr.check_compatibility(g, h)


def test_merge():
    exp = gr.Graph()
    gr.add_step(exp, "c", "op_c", "a", "b")
    gr.add_step(exp, "e", "op_e", "c", "d")

    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    h = gr.Graph()
    gr.add_step(h, "e", "op_e", "c", "d")

    res = gr.merge(g, h)
    assert res == exp


def test_merge_and_execute():
    exp = gr.Graph()
    gr.add_step(exp, "c", "op_c", "a", "b")
    gr.add_step(exp, "e", "op_e", "c", "d")

    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    h = gr.Graph()
    gr.add_step(h, "e", "op_e", "c", "d")
    g = gr.merge(g, h)
    gr.finalize_definition(g)

    gr.update_internal_context(
        g,
        {
            "a": 1,
            "b": 2,
            "d": 4,
            "op_c": lambda x, y: x + y,
            "op_e": lambda x, y: x * y,
        },
    )
    gr.execute_to_targets(g, "e")

    assert g["e"] == 12


def test_get_subgraph():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    h = gr.get_subgraph(g, {"g", "e", "f", "op_g"})
    gr.set_internal_context(h, {"e": 1, "f": 2, "op_g": lambda x, y: x + y})
    gr.execute_to_targets(h, "g")
    assert h["g"] == 3
