import pytest
import qflow

def test_simple():
    g = qflow.Graph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_node("d")
    g.add_node("op_e")
    g.add_node("op_f")
    g.add_node("op_g")
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")

    res = qflow.execute_graph_from_context(g, {"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y}, "g")
    assert res["g"] == -9

def test_simplified_input():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")

    res = qflow.execute_graph_from_context(g, {"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y}, "g")
    assert res["g"] == -9

def test_diamond():
    g = qflow.Graph()
    g.add_node(("a"))
    g.add_node("b", "op_b", "a")
    g.add_node("c", "op_c", "b")
    g.add_node("d", "op_d", "b")
    g.add_node("e", "op_e", "c", "d")

    res = qflow.execute_graph_from_context(g, {"a":1, "op_b": lambda x: 2*x, "op_c": lambda x: 2*x, "op_d": lambda x: 2*x, "op_e": lambda x,y : x-y}, "e")
    assert res["e"] == 0

def test_graphviz():
    g = qflow.Graph(name = "graph1")
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    gv = g.get_graphviz_digraph()
    gv.view()

def test_graphviz_with_values():
    g = qflow.Graph(name = "graph_values")
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    g.set_internal_state({"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y})
    gv = g.get_graphviz_digraph()
    gv.view()

def test_graphviz_attrs():
    g = qflow.Graph(name = "graph2")
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    gv = g.get_graphviz_digraph(rankdir = "LR")
    gv.view()

if __name__ == "__main__":
    test_simple()
    test_simplified_input()
    test_diamond()
    test_graphviz()
    test_graphviz_with_values()
    test_graphviz_attrs()