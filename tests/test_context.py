"""
Tests of context functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Context
def test_set_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert g["op_b"] == operations["op_b"]
    assert g["op_c"] == operations["op_c"]
    assert g["a"] == operations["a"]


# Context
def test_get_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert gr.get_internal_context(g) == operations


# Context
def test_update_internal_context():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)
    assert g["a"] == 5

    new_operations = {"op_b": lambda x: 3 * x, "op_c": lambda x: 4 * x}
    gr.update_internal_context(g, new_operations)

    assert g["a"] == 5  # Unchanged
    assert g["op_b"] == new_operations["op_b"]  # Updated


# Context
def test_clear_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5})
    assert gr.get_has_value(g, "a")
    assert g["a"] == 5

    gr.clear_values(g)

    assert not gr.get_has_value(g, "a")
    assert gr.get_has_value(g, "op_b")  # Frozen
    assert gr.get_has_value(g, "op_c")


# Context
def test_get_list_of_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_list_of_values(g, ["a", "b"]) == [5, 10]


# Context
def test_get_dict_of_values():
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_dict_of_values(g, ["a", "b"]) == {"a": 5, "b": 10}


# Context
def test_get_kwargs_values():
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 2})
    assert gr.get_kwargs_values(g, {"exponent": "b"}) == {"exponent": 2}
