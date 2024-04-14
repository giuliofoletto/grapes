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
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.add_step("h", "op_h", "e")
    g.add_simple_conditional("j", "i", "g", "h")
    g.add_simple_conditional("l", "k", "g", "h")
    g.finalize_definition()

    context = {"e": 1, "f": 1, "i": True}
    g.set_internal_context(context)

    result_g = gr.get_path_to_target(g, "g")
    result_h = gr.get_path_to_target(g, "h")
    result_j = gr.get_path_to_target(g, "j")
    result_l = gr.get_path_to_target(g, "l")

    assert result_g == {"g", "op_g", "e", "f"}
    assert result_h == {"h", "op_h", "e"}
    assert result_j == {"j", "i", "g", "op_g", "e", "f"}
    assert result_l == {"l", "k", "g", "op_g", "e", "f", "h", "op_h"}
