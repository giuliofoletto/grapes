"""
Tests of visualization.
In many tests, the source of a graphviz graph is compared to an expected value stored in a pickle (pkl) file.
To build a new test of this kind, simply insert a line like
expected_sources[name] = gv.source
just before the assertion. This populates the expected file with the graph produced by the test.
After running the test once (with pytest), remove that line, otherwise the test always passes.
Remember to use LF line endings in the pkl file.
"""
import pytest
import qflow
import qflow.visualize
import filecmp
import pickle

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
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    return g


def test_simple(expected_sources):
    g = build_graph()
    name = "simple"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]


def test_with_values(expected_sources):
    g = build_graph()
    g.set_internal_context({"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y})
    name = "with_values"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]


def test_attrs(expected_sources):
    g = build_graph()
    name = "attrs"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name, rankdir="LR")
    assert gv.source == expected_sources[name]


def test_no_operations(expected_sources):
    g = build_graph()
    name = "no_operations"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name, hide_operations=True)
    assert gv.source == expected_sources[name]


def test_save_and_render(expected_sources):
    g = build_graph()
    name = "simple"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    gv.save(directory=output_directory)
    assert filecmp.cmp(output_directory + "/" + name + ".gv", expected_directory + "/" + name + ".gv")
    gv.render(directory=output_directory)
    assert filecmp.cmp(output_directory + "/" + name + ".gv.pdf", expected_directory + "/" + name + ".gv.pdf")


def test_conditional(expected_sources):
    g = qflow.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    name = "conditional"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]


def test_simplify_dependency(expected_sources):
    g = build_graph()
    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    name = "presimplification"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]

    g.simplify_dependency("g", "f")
    name = "postsimplification"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]


def test_simplify_all_dependencies(expected_sources):
    g = build_graph()
    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    g.simplify_all_dependencies("g")
    name = "postallsimplification"
    gv = qflow.visualize.get_graphviz_digraph(g, name=name)
    assert gv.source == expected_sources[name]
