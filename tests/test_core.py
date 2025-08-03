"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


def test_get_set():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    g["a"] = 1
    g["b"] = 2
    assert g["a"] == 1
    assert g["b"] == 2
    assert not gr.get_has_value(g, "c")
    assert not gr.get_has_value(g, "op_c")


def test_equality():
    g1 = gr.Graph()
    gr.add_step(g1, "c", "op_c", "a", "b")
    g2 = gr.Graph()
    gr.add_step(g2, "c", "op_c", "a", "b")
    assert g1 == g2

    g3 = gr.Graph()
    gr.add_step(g3, "c", "op_c", "a", "b")
    gr.add_step(g3, "d", "op_d", "c")
    assert g1 != g3

    g4 = gr.Graph()
    gr.add_step(g4, "c", "op_c", "a", "b")
    g5 = gr.Graph()
    gr.add_step(g5, "c", "op_c", "b", "a")  # Different order
    assert g4 != g5

    g6 = gr.Graph()
    gr.add_step(g6, "c", "op_c", "a", "b")
    g7 = gr.Graph()
    gr.add_step(g7, "c", "op_c", "a", "b")
    g7["a"] = 1  # Different values
    assert g6 != g7
