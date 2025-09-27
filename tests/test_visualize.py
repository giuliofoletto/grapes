"""
This module contains tests of visualization.

In many tests, the source of a graphviz graph is compared to an expected value stored in a pickle (pkl) file.
To build a new test of this kind, simply insert a line like
expected_sources[name] = gr.write_string(gv)
just before the assertion. This populates the expected file with the graph produced by the test.
After running the test once (with pytest), remove that line, otherwise the test always passes.
Remember to use LF line endings in the pkl file.
"""

import filecmp
import pickle

import pytest

import grapes as gr

output_directory = "tests/visualizations"
expected_directory = "tests/expected"


@pytest.fixture(scope="module")
def expected_sources():
    with open(expected_directory + "/expected.pkl", "rb") as f:
        expected = pickle.load(f)
    yield expected
    with open(expected_directory + "/expected.pkl", "wb") as f:
        pickle.dump(expected, f, 0)


def build_graph():
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)
    return g


def test_simple(expected_sources):
    """
    Test visualizing a graph.
    """
    g = build_graph()
    name = "simple"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]


def test_with_values(expected_sources):
    """
    Test visualizing a graph with some values set.
    """
    g = build_graph()
    gr.set_internal_context(
        g,
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        },
    )
    name = "with_values"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]


def test_attrs(expected_sources):
    """
    Test visualizing a graph, with some attributes passed to the construction of the pygraphviz.AGraph object.
    """
    g = build_graph()
    name = "attrs"
    gv = gr.get_graphviz_digraph(g, rankdir="LR")
    assert gr.write_string(gv) == expected_sources[name]


def test_no_operations(expected_sources):
    """
    Test visualizing a graph, hiding recipe nodes.
    """
    g = build_graph()
    name = "no_operations"
    gv = gr.get_graphviz_digraph(g, hide_recipes=True)
    assert gr.write_string(gv) == expected_sources[name]


def test_save_dot(expected_sources):
    """
    Test saving a graph to a dot file.
    """
    g = build_graph()
    name = "simple"
    gv = gr.get_graphviz_digraph(g)
    gr.write_dotfile(gv, output_directory + "/" + name + ".gv")
    assert filecmp.cmp(
        output_directory + "/" + name + ".gv", expected_directory + "/" + name + ".gv"
    )
    # Note: as of 2024, dot no longer draws reproducible (to the binary level) pdf files
    # so we are no longer checking for equality of the drawn file


def test_conditional(expected_sources):
    """
    Test visualizing a graph with a conditional node.
    """
    g = gr.Graph()
    gr.add_simple_conditional(g, "d", "c", "a", "b")
    name = "conditional"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]


def test_simplify_dependency(expected_sources):
    """
    Test visualizing a graph before and after simplifying a dependency.
    """
    g = build_graph()
    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)

    name = "presimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]

    gr.simplify_dependency(g, "g", "f")
    name = "postsimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]


def test_simplify_all_dependencies(expected_sources):
    """
    Test visualizing a graph after simplifying all dependencies.
    """
    g = build_graph()
    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)

    gr.simplify_all_dependencies(g, "g")
    name = "postallsimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gr.write_string(gv) == expected_sources[name]


def test_color_by_generation(expected_sources):
    """
    Test visualizing a graph, coloring nodes by topological generation.
    """
    g = build_graph()
    gv = gr.get_graphviz_digraph(g, color_mode="by_generation", colormap="plasma")
    name = "color_by_generation"
    assert gr.write_string(gv) == expected_sources[name]


def test_color_sources_and_sinks(expected_sources):
    """
    Test visualizing a graph, coloring source and sink nodes.
    """
    g = build_graph()
    gv = gr.get_graphviz_digraph(g, color_mode="sources_and_sinks", colormap="plasma")
    name = "color_sources_and_sinks"
    assert gr.write_string(gv) == expected_sources[name]
