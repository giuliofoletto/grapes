import pytest
import qflow

def test_graphviz():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    gv = g.get_graphviz_digraph(name = "test_graphviz")
    gv.render()
    gv.save()

def test_graphviz_with_values():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    g.set_internal_state({"a":1, "b": 2, "f": 12, "op_e": lambda x,y : x+y, "op_f": lambda x,y : x*y, "op_g": lambda x,y : x-y})
    gv = g.get_graphviz_digraph(name = "test_graphviz_with_values")
    gv.render()
    gv.save()

def test_graphviz_attrs():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    gv = g.get_graphviz_digraph(name = "test_graphviz_attrs", rankdir = "LR")
    gv.render()
    gv.save()

def test_graphviz_no_operations():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")
    gv = g.get_graphviz_digraph(name = "test_graphviz_no_operations", hide_operations = True)
    gv.render()
    gv.save()

if __name__ == "__main__":
    test_graphviz()
    test_graphviz_with_values()
    test_graphviz_attrs()