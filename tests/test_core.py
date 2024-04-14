"""
Tests of core functionality.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest

import grapes as gr


# Design, context, evaluate
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

    g.update_internal_context(
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        }
    )
    g.execute_to_targets("g")

    assert g["g"] == -9


# Design, context, evaluate
def test_simplified_input():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()

    g.update_internal_context(
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        }
    )
    g.execute_to_targets("g")

    assert g["g"] == -9


# Design, context, evaluate
def test_diamond():
    g = gr.Graph()
    g.add_step("a")
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.add_step("d", "op_d", "b")
    g.add_step("e", "op_e", "c", "d")
    g.finalize_definition()

    g.update_internal_context(
        {
            "a": 1,
            "op_b": lambda x: 2 * x,
            "op_c": lambda x: 2 * x,
            "op_d": lambda x: 2 * x,
            "op_e": lambda x, y: x - y,
        }
    )
    g.execute_to_targets("e")

    assert g["e"] == 0


# Design, context, evaluate
def test_inverted_input():
    # Typically, we proceed from bottom to top
    # Here we test the opposite
    g = gr.Graph()
    g.add_step("c", "op_c", "b")
    g.add_step("b", "op_b", "a")
    g.finalize_definition()

    g.update_internal_context(
        {"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x}
    )
    g.execute_to_targets("c")

    assert g["c"] == 6


# Design, context, evaluate
def test_conditional():
    g = gr.Graph()
    g.add_simple_conditional("d", "c", "a", "b")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": True})
    g.execute_to_targets("d")

    assert g["d"] == g["a"]


# Design, merge
def test_compatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("e", "op_e", "c", "d")
    assert h.is_compatible(g)


# Design, merge
def test_incompatibility():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    h = gr.Graph()
    h.add_step("c", "op_c2", "a", "d")
    assert not h.is_compatible(g)


# Design, merge
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


# Design, merge, context, evaluate
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

    g.update_internal_context(
        {"a": 1, "b": 2, "d": 4, "op_c": lambda x, y: x + y, "op_e": lambda x, y: x * y}
    )
    g.execute_to_targets("e")

    assert g["e"] == 12


# Design, context, evaluate
def test_kwargs():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", exponent="b")
    g.finalize_definition()

    def example_exponentiation_func(base, exponent):
        return base**exponent

    g.update_internal_context({"a": 5, "b": 2, "op_c": example_exponentiation_func})
    g.execute_to_targets("c")

    assert g["c"] == 25


# Design, context, simplify, evaluate
def test_simplify_dependency():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    g.simplify_dependency("g", "f")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    g.execute_to_targets("g")

    assert g["g"] == -9


# Design, context, simplify, evaluate
def test_simplify_all_dependencies():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    g.set_internal_context(operations)

    g.simplify_all_dependencies("g")
    g.finalize_definition()

    g.update_internal_context({"a": 1, "b": 2, "c": 3, "d": 4})
    g.execute_to_targets("g")

    assert g["g"] == -9


# Design, context, evaluate
def test_progress_towards_targets():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("f", "op_f", "b", "c", "e")
    g.add_step("e", "op_e", "d")

    context = {
        "op_b": lambda x: 2 * x,
        "op_e": lambda x: 3 * x,
        "op_f": lambda x, y, z: x + y + z,
        "a": 5,
        "d": 4,
    }
    g.set_internal_context(context)
    g.finalize_definition()

    # f cannot be reached because c is not in context, but b and e can be computed
    g.progress_towards_targets("f")
    assert g["b"] == 10
    assert g["e"] == 12


# Design, context, evaluate
def test_multiple_conditional():
    g = gr.Graph()
    g.add_multiple_conditional(
        "result",
        ["condition_1", "condition_2", "condition_3"],
        ["node_1", "node_2", "node_3"],
    )
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


# Design, context, evaluate
def test_multiple_conditional_with_default():
    g = gr.Graph()
    g.add_multiple_conditional(
        "result",
        ["condition_1", "condition_2", "condition_3"],
        ["node_1", "node_2", "node_3", "node_default"],
    )
    context = {
        "condition_1": False,
        "condition_2": False,
        "condition_3": False,
        "node_1": 1,
        "node_2": 2,
        "node_3": 3,
        "node_default": 4,
    }
    g.set_internal_context(context)
    g.finalize_definition()

    g.execute_to_targets("result")

    assert g["result"] == 4


# Design, context, evaluate
def test_edit_step():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.set_internal_context({"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x})
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


# Design, context, evaluate
def test_remove_step():
    g = gr.Graph()
    g.add_step("b", "op_b", "a")
    g.add_step("c", "op_c", "b")
    g.set_internal_context({"a": 1, "op_b": lambda x: 2 * x, "op_c": lambda x: 3 * x})
    g.finalize_definition()

    g.remove_step("b")
    with pytest.raises(KeyError):
        g["b"]
    with pytest.raises(ValueError):
        g.remove_step("d")


# Design, context, evaluate
def test_add_step_quick():
    def example_function_only_positional(a, b):
        return a**b

    def example_function_with_kw_only_args(a, b, *, c):
        return a**b + c

    def example_function_with_no_args():
        return 1

    g = gr.Graph()
    g.add_step_quick("c", example_function_only_positional)
    g.add_step_quick("d", example_function_with_kw_only_args)
    g.add_step_quick("e", example_function_with_no_args)
    g.add_step_quick("f", lambda e: 2 * e)
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


# Design
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


# Design, context, reachability
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


# Design, context, reachability
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


# Design, context, reachability
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


# Design, context, reachability
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


# Design, context, reachability
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


# Design, context, reachability
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


# Design, features
def test_sources_and_sinks():
    g = gr.Graph()
    g.add_step("c", "op_c", "a", "b")
    g.add_step("e", "op_e", "d")
    g.add_step("op_c", "b_op_c", "d_op_c")
    g.finalize_definition()

    assert g.get_all_sources(exclude_recipes=True) == {"a", "b", "d"}
    assert g.get_all_sources(exclude_recipes=False) == {
        "a",
        "b",
        "d",
        "b_op_c",
        "d_op_c",
        "op_e",
    }
    assert g.get_all_sinks(exclude_recipes=True) == {"c", "e"}
    assert g.get_all_sinks(exclude_recipes=False) == {"c", "e"}


# Design, evaluate
def test_execute_towards_conditions():
    """
    Execute towards the conditions of conditional by computing c2.
    """
    g = gr.Graph()
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = True
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    g.execute_towards_conditions("c1", "c2", "c3")

    assert not g.has_value("c1")
    assert not g.has_value("c3")
    assert g["c2"] == True


# Design, evaluate
def test_execute_towards_all_conditions_of_conditional():
    """
    Execute towards the conditions of conditional by computing c2 (the conditional is passed instead of the conditions).
    """
    g = gr.Graph()
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = True
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    g.execute_towards_all_conditions_of_conditional("conditional")

    assert not g.has_value("c1")
    assert not g.has_value("c3")
    assert g["c2"] == True


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step():
    """
    Convert conditional to a trivial step since its condition c2 already has true value.
    """
    g = gr.Graph()
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["c2"] = True
    g["v2"] = 2
    g.finalize_definition()

    g.convert_conditional_to_trivial_step("conditional")
    assert g.get_type("conditional") == "standard"

    g.execute_to_targets("conditional")
    assert g["conditional"] == g["v2"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_with_evaluation():
    """
    Convert conditional to a trivial step but compute the conditions.
    """
    g = gr.Graph()
    g.add_step("v2", "identity_recipe", "pre_v2")
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = True
    g["pre_v2"] = 2
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    g.convert_conditional_to_trivial_step(
        "conditional", execute_towards_conditions=True
    )
    assert g.get_type("conditional") == "standard"

    g.execute_to_targets("conditional")
    assert g["conditional"] == g["v2"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_with_default():
    """
    Convert conditional to a trivial step, computing conditions, but use default value since no condition is true.
    """
    g = gr.Graph()
    g.add_step("default", "identity_recipe", "pre_default")
    g.add_step("c", "identity_recipe", "pre_c")
    g.add_multiple_conditional("conditional", ["c"], ["v", "default"])
    g["pre_c"] = False
    g["pre_default"] = 1
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    g.convert_conditional_to_trivial_step(
        "conditional", execute_towards_conditions=True
    )
    assert g.get_type("conditional") == "standard"

    g.execute_to_targets("conditional")
    assert g["conditional"] == g["default"]


# Design, simplify, evaluate
def test_convert_conditional_to_trivial_step_without_true_values():
    """
    Try to convert conditional to trivial step but no conditions can be evaluated to true.
    """
    g = gr.Graph()
    g.add_step("v2", "identity_recipe", "pre_v2")
    g.add_step("c2", "identity_recipe", "pre_c2")
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g["pre_c2"] = False
    g["pre_v2"] = 2
    g["identity_recipe"] = lambda x: x
    g.finalize_definition()

    with pytest.raises(ValueError):
        g.convert_conditional_to_trivial_step(
            "conditional", execute_towards_conditions=True
        )


# Design, features
def test_get_all_conditionals():
    """
    Get set of all conditionals in the graph.
    """
    g = gr.Graph()
    g.add_simple_conditional("conditional1", "c1", "vt", "vf")
    g.add_simple_conditional("conditional2", "c2", "vt", "vf")
    g.finalize_definition()

    assert g.get_all_conditionals() == {"conditional1", "conditional2"}


# Design, simplify, evaluate
def test_convert_all_conditionals_to_trivial_steps():
    """
    Convert all conditionals to trivial steps.
    """
    g = gr.Graph()
    g.add_simple_conditional("conditional1", "c1", "vt", "vf")
    g.add_simple_conditional("conditional2", "c2", "vt", "vf")
    g["c1"] = True
    g["c2"] = False
    g["vt"] = 1
    g["vf"] = 2
    g.finalize_definition()

    g.convert_all_conditionals_to_trivial_steps()
    assert g.get_type("conditional1") == "standard"
    assert g.get_type("conditional2") == "standard"

    g.execute_to_targets("conditional1", "conditional2")
    assert g["conditional1"] == g["vt"]
    assert g["conditional2"] == g["vf"]


# Design, simplify, evaluate
def test_convert_all_conditionals_to_trivial_steps_with_evaluation():
    """
    Convert all conditionals to trivial steps, computing the conditions.
    """
    g = gr.Graph()
    g.add_multiple_conditional("conditional", ["c1", "c2", "c3"], ["v1", "v2", "v3"])
    g.add_step("c1", "op_id", "pre_c1")
    g.add_step("c2", "op_id", "pre_c2")
    g.add_step("c3", "op_id", "pre_c3")
    g["pre_c1"] = True
    g["pre_c2"] = False
    g["pre_c3"] = False
    g["op_id"] = lambda x: x
    g["v1"] = 1
    g["v2"] = 2
    g["v3"] = 3
    g.finalize_definition()

    g.convert_all_conditionals_to_trivial_steps(execute_towards_conditions=True)
    assert g.get_type("conditional") == "standard"

    g.execute_to_targets("conditional")
    assert g["conditional"] == g["v1"]


# Design, context, util, evaluate
def test_get_subgraph():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.finalize_definition()

    h = g.get_subgraph({"g", "e", "f", "op_g"})
    h.set_internal_context({"e": 1, "f": 2, "op_g": lambda x, y: x + y})
    h.execute_to_targets("g")
    assert h["g"] == 3


# Design, features
def test_get_all_ancestors():
    g = gr.Graph()
    g.add_step("e", "op_e", "a", "b")
    g.add_step("f", "op_f", "c", "d")
    g.add_step("g", "op_g", "e", "f")
    g.add_step("h", "op_h", "e")
    g.add_simple_conditional("j", "i", "g", "h")
    g.finalize_definition()

    result_g = g.get_all_ancestors_target("g")
    result_h = g.get_all_ancestors_target("h")
    result_j = g.get_all_ancestors_target("j")

    assert result_g == {"op_g", "e", "f", "op_f", "c", "d", "op_e", "a", "b"}
    assert result_h == {"op_h", "e", "op_e", "a", "b"}
    assert result_j == {
        "i",
        "h",
        "op_h",
        "g",
        "op_g",
        "e",
        "f",
        "op_f",
        "c",
        "d",
        "op_e",
        "a",
        "b",
    }


# Design
def test_make_recipe_dependencies_also_recipes():
    g = gr.Graph()
    g.add_step("a", "op_a", "b")
    g.add_step("op_a", "build_op_a", "c", "d")  # c and d will be converted to recipes
    g.add_step("b", "op_b", "c")  # c will no longer be converted to recipe
    g.finalize_definition()  # calls make_recipe_dependencies_also_recipes

    assert g.is_recipe("d")
    assert not g.is_recipe("c")
