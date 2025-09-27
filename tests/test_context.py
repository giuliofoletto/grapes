"""
This module contains tests of context functionality.
"""

import pytest

import grapes as gr


def test_set_internal_context():
    """
    Test setting the internal context of a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert g["op_b"] == operations["op_b"]
    assert g["op_c"] == operations["op_c"]
    assert g["a"] == operations["a"]


def test_get_internal_context():
    """
    Test getting the internal context of a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    gr.finalize_definition(g)

    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x, "a": 5}
    gr.set_internal_context(g, operations)

    assert gr.get_internal_context(g) == operations


def test_update_internal_context():
    """
    Test setting and then updating the internal context of a graph.
    """
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


def test_clear_values():
    """
    Test clearing values in a graph, verifying also behavior with frozen values.
    """
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


def test_get_list_of_values():
    """
    Test getting a list of values from a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_list_of_values(g, ["a", "b"]) == [5, 10]


def test_get_dict_of_values():
    """
    Test getting a dictionary of values from a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "op_b", "a")
    gr.add_step(g, "c", "op_c", "b")
    operations = {"op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 10})
    assert gr.get_dict_of_values(g, ["a", "b"]) == {"a": 5, "b": 10}


def test_get_kwargs_values():
    """
    Test getting kwargs values from a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", exponent="b")
    gr.finalize_definition(g)

    gr.update_internal_context(g, {"a": 5, "b": 2})
    assert gr.get_kwargs_values(g, {"exponent": "b"}) == {"exponent": 2}


def test_update_recipes_from_module():
    """
    Test updating recipes from a module in a graph, verifying also proper execution.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "d", "op_d", "c")
    gr.finalize_definition(g)

    # Example module with functions
    import data.example_module as functions

    gr.update_recipes_from_module(g, functions)

    assert g["op_c"] == functions.op_c
    assert g["op_d"] == functions.op_d

    gr.update_internal_context(g, {"a": 5, "b": 2})
    gr.execute_to_targets(g, "d")
    assert g["c"] == 7
    assert g["d"] == 14
