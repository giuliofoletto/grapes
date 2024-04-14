"""
Tests of visualization.

In many tests, the source of a graphviz graph is compared to an expected value stored in a pickle (pkl) file.
To build a new test of this kind, simply insert a line like
expected_sources[name] = gv.string()
just before the assertion. This populates the expected file with the graph produced by the test.
After running the test once (with pytest), remove that line, otherwise the test always passes.
Remember to use LF line endings in the pkl file.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
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
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()
    return g


def test_simple(expected_sources):
    g = build_graph()
    name = "simple"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]


def test_with_values(expected_sources):
    g = build_graph()
    g.set_internal_context(
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        }
    )
    name = "with_values"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]


def test_attrs(expected_sources):
    g = build_graph()
    name = "attrs"
    gv = gr.get_graphviz_digraph(g, rankdir="LR")
    assert gv.string() == expected_sources[name]


def test_no_operations(expected_sources):
    g = build_graph()
    name = "no_operations"
    gv = gr.get_graphviz_digraph(g, hide_recipes=True)
    assert gv.string() == expected_sources[name]


def test_save_dot(expected_sources):
    g = build_graph()
    name = "simple"
    gv = gr.get_graphviz_digraph(g)
    gv.write(output_directory + "/" + name + ".gv")
    assert filecmp.cmp(
        output_directory + "/" + name + ".gv", expected_directory + "/" + name + ".gv"
    )
    # Note: as of 2024, dot no longer draws reproducible (to the binary level) pdf files
    # so we are no longer checking for equality of the drawn file


def test_conditional(expected_sources):
    g = gr.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    name = "conditional"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]


def test_simplify_dependency(expected_sources):
    g = build_graph()
    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    name = "presimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]

    gr.simplify_dependency(g, "g", "f")
    name = "postsimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]


def test_simplify_all_dependencies(expected_sources):
    g = build_graph()
    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    gr.simplify_all_dependencies(g, "g")
    name = "postallsimplification"
    gv = gr.get_graphviz_digraph(g)
    assert gv.string() == expected_sources[name]


def test_color_by_generation(expected_sources):
    g = build_graph()
    gv = gr.get_graphviz_digraph(g, color_mode="by_generation", colormap="plasma")
    name = "color_by_generation"
    assert gv.string() == expected_sources[name]


def test_color_sources_and_sinks(expected_sources):
    g = build_graph()
    gv = gr.get_graphviz_digraph(g, color_mode="sources_and_sinks", colormap="plasma")
    name = "color_sources_and_sinks"
    assert gv.string() == expected_sources[name]
