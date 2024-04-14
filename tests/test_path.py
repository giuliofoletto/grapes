"""
Tests of path functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, context, path
def test_get_path_to_target():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.add_step(g, "h", "op_h", "e")
    gr.add_simple_conditional(g, "j", "i", "g", "h")
    gr.add_simple_conditional(g, "l", "k", "g", "h")
    gr.finalize_definition(g)

    context = {"e": 1, "f": 1, "i": True}
    gr.set_internal_context(g, context)

    result_g = gr.get_path_to_target(g, "g")
    result_h = gr.get_path_to_target(g, "h")
    result_j = gr.get_path_to_target(g, "j")
    result_l = gr.get_path_to_target(g, "l")

    assert result_g == {"g", "op_g", "e", "f"}
    assert result_h == {"h", "op_h", "e"}
    assert result_j == {"j", "i", "g", "op_g", "e", "f"}
    assert result_l == {"l", "k", "g", "op_g", "e", "f", "h", "op_h"}
