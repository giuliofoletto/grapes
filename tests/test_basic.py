"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest
import grapes as gr
import warnings


def test_simple():
    g = gr.Graph()
    g.add_step("a")
    g.add_step("b")
    g.add_step("c")
    g.add_step("d")
    g.add_step("op_e")
    g.add_step("op_f")
    g.add_step("op_g")
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y})
    g.execute_to_targets("g")

    assert g["g"] == -9


def test_simplified_input():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "f": 12, "op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y})
    g.execute_to_targets("g")

    assert g["g"] == -9


def test_diamond():
    g = gr.Graph()
    g.add_step("a")
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.add_step("d", "op_d", "b")
    g.add_step("e", "op_e", "c", "d")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 2*x, "op_d": lambda x: 2*x, "op_e": lambda x, y: x-y})
    g.execute_to_targets("e")

    assert g["e"] == 0


def test_inverted_input():
    # Typically, we proceed from bottom to top
    # Here we test the opposite
    g = gr.Graph()
    g.add_step("c", "op_c", "b")
    g.add_step("b", "op_b", "a")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 3*x})
    g.execute_to_targets("c")

    assert g["c"] == 6


def test_conditional():
    g = gr.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": True})
    g.execute_to_targets("d")

    assert g["d"] == g["a"]


def test_compatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    assert h.is_compatible(g)


def test_incompatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("c", "op_c2", "a", "d")
    assert not h.is_compatible(g)


def test_merge():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    g.merge(h)

    assert g == exp


def test_merge_and_execute():
    exp = gr.Graph()
    exp.add_step("c", "op_c", "a", "b")
    exp.add_step("e", "op_e", "c", "d")

    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    g.merge(h)
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "d": 4, "op_c": lambda x, y: x+y, "op_e": lambda x, y: x*y})
    g.execute_to_targets("e")

    assert g["e"] == 12


def test_kwargs():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", exponent="b")
    g.finalize_definition()

    def example_exponentiation_func(base, exponent):
        return base**exponent

    g.update_internal_context({"a": 5, "b": 2, "op_c": example_exponentiation_func})
    g.execute_to_targets("c")

    assert g["c"] == 25


def test_wrap_with_function():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)
    g.finalize_definition()

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(g, ["a", "b", "c", "d"], "g", input_as_kwargs=False)
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(g, ["a", "b", "c", "d"], "e", "f", "g", input_as_kwargs=False)
    assert f1(1, 2, 3, 4) == -9
    assert f2(1, 2, 3, 4) == [3, 12, -9]


def test_lambdify():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)
    g.finalize_definition()

    # Get a function a,b,c,d -> g
    f1 = gr.lambdify_graph(g, ["a", "b", "c", "d"], "g")
    assert f1(a=1, b=2, c=3, d=4) == -9


def test_simplify_dependency():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    g.simplify_dependency("g", "f")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    g.execute_to_targets("g")

    assert g["g"] == -9


def test_simplify_all_dependencies():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {"op_e": lambda x, y: x+y, "op_f": lambda x, y: x*y, "op_g": lambda x, y: x-y}
    g.set_internal_context(operations)

    g.simplify_all_dependencies("g")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    g.execute_to_targets("g")

    assert g["g"] == -9


def test_progress_towards_targets():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("f", "op_f", "b", "c", "e")
    g.add_step("e", "op_e", "d")

    context = {"op_b": lambda x: 2*x, "op_e": lambda x: 3*x, "op_f": lambda x, y, z: x + y + z, "a": 5, "d": 4}
    g.set_internal_context(context)
    g.finalize_definition()

    # f cannot be reached because c is not in context, but b and e can be computed
    g.progress_towards_targets("f")
    assert g["b"] == 10
    assert g["e"] == 12


def test_multiple_conditional():
    g = gr.Graph()
    g.add_multiple_conditional("result", ["condition_1", "condition_2", "condition_3"], ["node_1", "node_2", "node_3"])
    context = {
        "condition_1": False,
        "condition_2": True,
        "condition_3": False,
        "node_1": 1,
        "node_2": 2,
        "node_3": 3,
    }
    g.set_internal_context(context)
    g.finalize_definition()

    g.execute_to_targets("result")

    assert g["result"] == 2


def test_multiple_conditional_with_default():
    g = gr.Graph()
    g.add_multiple_conditional("result", ["condition_1", "condition_2", "condition_3"], ["node_1", "node_2", "node_3", "node_default"])
    context = {
        "condition_1": False,
        "condition_2": False,
        "condition_3": False,
        "node_1": 1,
        "node_2": 2,
        "node_3": 3,
        "node_default": 4
    }
    g.set_internal_context(context)
    g.finalize_definition()

    g.execute_to_targets("result")

    assert g["result"] == 4


def test_edit_step():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.set_internal_context({"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 3*x})
    g.finalize_definition()

    g.execute_to_targets("c")
    assert g["b"] == 2
    assert g["c"] == 6

    g.edit_step("b", "new_op_b", "a", "d")
    assert g["b"] == 2  # Value is unchanged
    assert g["c"] == 6  # Value is unchanged

    g.clear_values("b", "c")
    g.update_internal_context({"d": 3, "new_op_b": lambda x, y: x + y})
    g.finalize_definition()

    g.execute_to_targets("c")
    assert g["b"] == 4
    assert g["c"] == 12


def test_remove_step():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.set_internal_context({"a": 1, "op_b": lambda x: 2*x, "op_c": lambda x: 3*x})
    g.finalize_definition()

    g.remove_step("b")
    with pytest.raises(KeyError):
        g["b"]
    with pytest.raises(ValueError):
        g.remove_step("d")


def test_add_step_quick():
    def example_function_only_positional(a, b):
        return a**b

    def example_function_with_kw_only_args(a, b, *, c):
        return a**b+c

    def example_function_with_no_args():
        return 1

    g = gr.Graph()
    g.add_step_quick("c", example_function_only_positional)
    g.add_step_quick("d", example_function_with_kw_only_args)
    g.add_step_quick("e", example_function_with_no_args)
    g.add_step_quick("f", lambda e: 2*e)
    g.update_internal_context({"a": 2, "b": 3})
    g.finalize_definition()

    g.execute_to_targets("d", "f")  # "c" and "e" should be automatically computed
    assert g["c"] == 8
    assert g["d"] == 16
    assert g["e"] == 1
    assert g["f"] == 2

    def example_function_with_varargs(*args):
        return 1

    with pytest.raises(ValueError):
        g.add_step_quick("g", example_function_with_varargs)
    with pytest.raises(TypeError):
        g.add_step_quick("h", "a non-function object")


def test_topological_generations():
    g = gr.Graph()
    g.add_step("d", "fd", "b", "c")
    g.add_step("b", "fb", "a")
    g.finalize_definition()

    assert g.get_node_attribute("a", "topological_generation_index") == 0
    assert g.get_node_attribute("b", "topological_generation_index") == 1
    assert g.get_node_attribute("c", "topological_generation_index") == 0
    assert g.get_node_attribute("d", "topological_generation_index") == 2
    assert g.get_node_attribute("fb", "topological_generation_index") == 0
    assert g.get_node_attribute("fd", "topological_generation_index") == 0


def test_reachability_simple():
    g = gr.Graph()
    g.add_step("b", "fb", "a")
    g["fb"] = lambda a: a
    g.finalize_definition()

    g.find_reachability_targets("b")
    assert g.get_reachability("b") == "unreachable"
    g.clear_reachabilities()

    g.update_internal_context({"a": 1})
    g.find_reachability_targets("b")
    assert g.get_reachability("b") == "reachable"


def test_reachability_long_graph():
    g = gr.Graph()
    g.add_step_quick("c", lambda b: b)
    g.add_step_quick("b", lambda a: a)
    g.finalize_definition()

    g.find_reachability_targets("b")
    assert g.get_reachability("b") == "unreachable"
    g.clear_reachabilities()

    g.update_internal_context({"a": 1})
    g.find_reachability_targets("b")
    assert g.get_reachability("b") == "reachable"


def test_reachability_conditional_with_true_value():
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g["condition"] = True
    g.finalize_definition()

    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    g.update_internal_context({"value_true": 1})
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "reachable"


def test_reachability_multiple_conditional_with_true_value():
    g = gr.Graph()
    g.add_multiple_conditional("name", ["ca", "cb"], ["a", "b", "c"])
    g["ca"] = True
    g.finalize_definition()

    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    g.update_internal_context({"a": 1})
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "reachable"


def test_conditional_no_conditions_defined():
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g.add_step_quick("condition", lambda pre_req: pre_req)
    g.finalize_definition()

    # Here, condition and possibilities are unreachable
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    # Here, condition is undefined but reachable, but all values are unreachable
    g["pre_req"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["value_true"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "uncertain"
    g.clear_reachabilities()

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["value_false"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "reachable"


def test_multiple_conditional_no_conditions_defined():
    g = gr.Graph()
    g.add_multiple_conditional("name", ["ca", "cb"], ["va", "vb", "vc"])
    g.add_step_quick("ca", lambda pa: pa)
    g.add_step_quick("cb", lambda pb: pb)
    g.finalize_definition()

    # Here, condition and possibilities are unreachable
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    # Here, ca is undefined but reachable, but all values are unreachable
    g["pa"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "unreachable"
    g.clear_reachabilities()

    # Now one of the possibilities is already available, therefore the conditional might be, depending on condition
    g["va"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "uncertain"
    g.clear_reachabilities()

    # Now all of the possibilities are reachable, but the conditional is still uncertain because we do not know which condition is True
    g["pb"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "uncertain"
    g.clear_reachabilities()

    # Now all of the possibilities are already available, therefore the conditional is certainly reachable
    g["vb"] = 1
    g["vc"] = 1
    g.find_reachability_targets("name")
    assert g.get_reachability("name") == "reachable"


def test_execution_with_feasibility_check():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_step("b", "fb", "a")
    g["fb"] = lambda a: a
    g.finalize_definition()

    # a is not available
    with pytest.raises(ValueError):
        gr.execute_graph_from_context(g, {}, "b")
    # Now a becomes available
    res = gr.execute_graph_from_context(g, {"a": 1}, "b")
    assert res["b"] == 1


def test_execution_with_feasibility_check_uncertain():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_simple_conditional("name", "condition", "value_true", "value_false")
    g.add_step_quick("condition", lambda pre_req: pre_req)
    g["pre_req"] = True
    g["value_true"] = 1
    g.finalize_definition()

    # Reachability is uncertain because condition is reachable and one value also is
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = gr.execute_graph_from_context(g, {}, "name")
        assert len(w) == 1
        # But the computation is actually feasible
        assert res["name"] == 1


def test_unfeasible_wrap():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_step("d", "op_d", "a", "b", "c")
    g["op_d"] = lambda a, b, c: a + b + c
    g.finalize_definition()

    with pytest.raises(ValueError):
        # Pass b as input, c as constant, but do not pass a
        f1 = gr.wrap_graph_with_function(g, ["b"], "d", constants={"c": 1}, input_as_kwargs=False)
    # Pass also a
    f2 = gr.wrap_graph_with_function(g, ["a", "b"], "d", constants={"c": 1}, input_as_kwargs=False)
    assert f2(1, 1) == 3


def test_sources_and_sinks():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    g.add_step("e", "op_e", "d")
    g.add_step("op_c", "b_op_c", "d_op_c")
    g.finalize_definition()

    assert g.get_all_sources(exclude_recipes=True) == {"a", "b", "d"}
    assert g.get_all_sources(exclude_recipes=False) == {"a", "b", "d", "b_op_c", "d_op_c", "op_e"}
    assert g.get_all_sinks(exclude_recipes=True) == {"c", "e"}
    assert g.get_all_sinks(exclude_recipes=False) == {"c", "e"}


def test_execution_of_all_graph():
    # TODO use separate test suite for test of utils
    g = gr.Graph()
    g.add_step("c", "f_c", "a", "b")
    g.add_step("f", "f_f", "d", "e")
    g["f_c"] = lambda a, b: a + b
    g["f_f"] = lambda d, e: d * e
    g.finalize_definition()

    # No target means that everything is a target
    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "d": 3, "e": 4})
    assert res["c"] == 3
    assert res["f"] == 12
