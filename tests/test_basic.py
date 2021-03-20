import pytest
import qflow


def test_simple():
    g = qflow.Graph()
    g.add_placeholder("a")
    g.add_placeholder("b")
    g.add_placeholder("c")
    g.add_placeholder("d")
    g.add_placeholder("op_e")
    g.add_placeholder("op_f")
    g.add_placeholder("op_g")
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")

    res = qflow.execute_graph_from_context(g, {"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}, "g")
    assert res["g"] == -9


def test_simplified_input():
    g = qflow.Graph()
    g.add_node("e", "op_e", "a", "b")
    g.add_node("f", "op_f", "c", "d")
    g.add_node("g", "op_g", "e", "f")

    res = qflow.execute_graph_from_context(g, {"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}, "g")
    assert res["g"] == -9


def test_diamond():
    g = qflow.Graph()
    g.add_placeholder("a")
    g.add_node("b", "op_b", "a")
    g.add_node("c", "op_c", "b")
    g.add_node("d", "op_d", "b")
    g.add_node("e", "op_e", "c", "d")

    res = qflow.execute_graph_from_context(g, {"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 2*x, "op_d": lambda x: 2*x, "op_e": lambda x, y: x-y}, "e")
    assert res["e"] == 0


def test_conditional():
    g = qflow.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    res = qflow.execute_graph_from_context(g, {"a": 1, "b": 2, "c": True}, "d")
    assert res["d"] == res["a"]


def test_compatibility():
    g = qflow.Graph()
    g.add_node("c", "op_c", "a", "b")
    h = qflow.Graph()
    h.add_node("e", "op_e", "c", "d")
    assert h.isCompatible(g)


def test_incompatibility():
    g = qflow.Graph()
    g.add_node("c", "op_c", "a", "b")
    h = qflow.Graph()
    h.add_node("c", "op_c2", "a", "d")
    assert not h.isCompatible(g)


def test_merge():
    res = qflow.Graph()
    res.add_node("c", "op_c", "a", "b")
    res.add_node("e", "op_e", "c", "d")

    g = qflow.Graph()
    g.add_node("c", "op_c", "a", "b")
    h = qflow.Graph()
    h.add_node("e", "op_e", "c", "d")
    g.merge(h)

    assert g == res


def test_kwargs():
    g = qflow.Graph()
    g.add_node("c", "op_c", "a", exponent="b")

    def example_exponentiation_func(base, exponent):
        return base**exponent
    res = qflow.execute_graph_from_context(g, {"a": 5, "b": 2, "op_c": example_exponentiation_func}, "c")
    assert res["c"] == 25
