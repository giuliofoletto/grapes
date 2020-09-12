import pytest
import qflow

def test_simple():
    g = qflow.Graph()
    g.add_node(qflow.Node("a"))
    g.add_node(qflow.Node("b"))
    g.add_node(qflow.Node("c"))
    g.add_node(qflow.Node("d"))
    g.add_node(qflow.Node("op_e"))
    g.add_node(qflow.Node("op_f"))
    g.add_node(qflow.Node("op_g"))
    g.add_node(qflow.Node("e", "op_e", "a", "b"))
    g.add_node(qflow.Node("f", "op_f", "c", "d"))
    g.add_node(qflow.Node("g", "op_g", "e", "f"))

    res = qflow.execute_graph_from_context(g, {"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y}, "g")
    assert res["g"] == -9

def test_simplified_input():
    g = qflow.Graph()
    g.add_node(qflow.Node("e", "op_e", "a", "b"))
    g.add_node(qflow.Node("f", "op_f", "c", "d"))
    g.add_node(qflow.Node("g", "op_g", "e", "f"))

    res = qflow.execute_graph_from_context(g, {"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y}, "g")
    assert res["g"] == -9

if __name__ == "__main__":
    test_simple()
    test_simplified_input()