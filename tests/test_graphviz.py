import pytest
import qflow
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
    gv = g.get_graphviz_digraph(name = name)
    assert gv.source == expected_sources[name]

def test_with_values(expected_sources):
    g = build_graph()
    g.set_internal_state({"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y})
    name = "with_values"
    gv = g.get_graphviz_digraph(name = name)
    assert gv.source == expected_sources[name]

def test_attrs(expected_sources):
    g = build_graph()
    name = "attrs"
    gv = g.get_graphviz_digraph(name = name, rankdir = "LR")
    assert gv.source == expected_sources[name]

def test_no_operations(expected_sources):
    g = build_graph()
    name = "no_operations"
    gv = g.get_graphviz_digraph(name = name, hide_operations = True)
    assert gv.source == expected_sources[name]

def test_save_and_render(expected_sources):
    g = build_graph()
    name = "simple"
    gv = g.get_graphviz_digraph(name = name)
    gv.save(directory = output_directory)
    assert filecmp.cmp(output_directory + "/" + name + ".gv", expected_directory + "/" + name + ".gv")
    gv.render(directory = output_directory)
    assert filecmp.cmp(output_directory + "/" + name + ".gv.pdf", expected_directory + "/" + name + ".gv.pdf")