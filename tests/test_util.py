"""
This module contains tests of utilities.
"""

import warnings

import pytest

import grapes as gr

data_directory = "tests/data"


def test_simple_execution():
    """
    Test the simple execution of a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "a")
    gr.add_step(g, "b")
    gr.add_step(g, "c")
    gr.add_step(g, "d")
    gr.add_step(g, "op_e")
    gr.add_step(g, "op_f")
    gr.add_step(g, "op_g")
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.finalize_definition(g)

    res = gr.execute_graph_from_context(
        g,
        {
            "a": 1,
            "b": 2,
            "f": 12,
            "op_e": lambda x, y: x + y,
            "op_f": lambda x, y: x * y,
            "op_g": lambda x, y: x - y,
        },
        "g",
    )

    assert res["g"] == -9


def test_execution_more_targets():
    """
    Test the execution of a graph to multiple targets.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    gr.add_step(g, "f", "op_f", "d", "e")
    g["op_c"] = lambda a, b: a + b
    g["op_f"] = lambda d, e: d * e
    gr.finalize_definition(g)

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "d": 3, "e": 4}, "c", "f")

    assert res["c"] == 3
    assert res["f"] == 12


def test_execution_inplace():
    """
    Test the inplace execution of a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    g["op_c"] = lambda a, b: a + b
    gr.finalize_definition(g)

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2}, "c", inplace=True)

    assert res["c"] == 3
    assert g["c"] == 3
    assert gr.get_internal_context(res) == gr.get_internal_context(g)


def test_execution_not_inplace_does_not_change_context():
    """
    Test that executing a graph not inplace does not change its context.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    g["op_c"] = lambda a, b: a + b
    gr.finalize_definition(g)

    current_context = gr.get_internal_context(g)

    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2}, "c", inplace=False)
    new_context = gr.get_internal_context(g)

    assert res["c"] == 3
    assert current_context == new_context


def test_execution_of_all_graph():
    """
    Test the execution of all nodes in a graph. TODO correct.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "f_c", "a", "b")
    gr.add_step(g, "f", "f_f", "d", "e")
    g["f_c"] = lambda a, b: a + b
    g["f_f"] = lambda d, e: d * e
    gr.finalize_definition(g)

    # No target means that everything is a target
    res = gr.execute_graph_from_context(g, {"a": 1, "b": 2, "d": 3, "e": 4})
    assert res["c"] == 3
    assert res["f"] == 12


def test_execution_with_feasibility_check():
    """
    Test the execution of a graph with feasibility check.
    """
    g = gr.Graph()
    gr.add_step(g, "b", "fb", "a")
    g["fb"] = lambda a: a
    gr.finalize_definition(g)

    # a is not available
    feasibility, missing_dependencies = gr.check_feasibility_of_execution(g, {}, "b")
    assert feasibility == "unreachable"
    assert missing_dependencies == set("a")
    with pytest.raises(ValueError):
        gr.execute_graph_from_context(g, {}, "b")
    # Now a becomes available
    feasibility, missing_dependencies = gr.check_feasibility_of_execution(
        g, {"a": 1}, "b"
    )
    assert feasibility == "reachable"
    assert missing_dependencies == set()
    res = gr.execute_graph_from_context(g, {"a": 1}, "b")
    assert res["b"] == 1


def test_execution_with_feasibility_check_uncertain():
    """
    Test the execution of a graph with feasibility check, where reachability is uncertain.
    """
    g = gr.Graph()
    gr.add_simple_conditional(g, "name", "condition", "value_true", "value_false")
    gr.add_step_quick(g, "condition", lambda pre_req: pre_req)
    g["pre_req"] = True
    g["value_true"] = 1
    gr.finalize_definition(g)

    # Reachability is uncertain because condition is reachable and one value also is
    feasibility, missing_dependencies = gr.check_feasibility_of_execution(g, {}, "name")
    assert feasibility == "uncertain"
    assert missing_dependencies == {
        "value_false"
    }  # Note that set("value_false") splits the string into chars
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = gr.execute_graph_from_context(g, {}, "name")
        assert len(w) == 1
        # But the computation is actually feasible
        assert res["name"] == 1


def test_json_from_graph():
    """
    Test generating a JSON string from a graph's context.
    """
    g = gr.Graph()
    gr.add_step(g, "c", "op_c", "a", "b")
    g["a"] = 1
    g["b"] = 2
    g["op_c"] = lambda a, b: a + b
    gr.finalize_definition(g)

    json_string = gr.json_from_graph(g)
    expected_string = '{\n    "a": 1,\n    "b": 2\n}'  # Spacing and separators are defined in the json_from_graph function

    assert json_string == expected_string


def test_context_from_json_file():
    """
    Test generating a context from a JSON file.
    """
    file_name = data_directory + "/example.json"
    context = gr.context_from_json_file(file_name)
    expected_context = {"a": 1, "b": 2, "c": "hello"}

    assert context == expected_context


def test_context_from_toml_file():
    """
    Test generating a context from a TOML file.
    """
    file_name = data_directory + "/example.toml"
    context = gr.context_from_toml_file(file_name)
    expected_context = {"a": 1, "b": 2, "c": "hello"}

    assert context == expected_context


def test_context_from_file():
    """
    Test generating a context from a file, in any of the supported formats.
    """
    expected_context = {"a": 1, "b": 2, "c": "hello"}

    file_name = data_directory + "/example.json"
    context = gr.context_from_file(file_name)
    assert context == expected_context

    file_name = data_directory + "/example.toml"
    context = gr.context_from_file(file_name)
    assert context == expected_context


def test_wrap_with_function_input_as_kwargs_output_as_dict():
    """
    Test wrapping a graph with a function, using kwargs as input and dict as output.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(
        g, ["a", "b", "c", "d"], "g", input_as_kwargs=True, output_as_dict=True
    )
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(
        g,
        ["a", "b", "c", "d"],
        "e",
        "f",
        "g",
        input_as_kwargs=True,
        output_as_dict=True,
    )
    assert f1(a=1, b=2, c=3, d=4) == -9
    assert f2(a=1, b=2, c=3, d=4) == dict(e=3, f=12, g=-9)


def test_wrap_with_function_input_as_kwargs_output_as_list():
    """
    Test wrapping a graph with a function, using kwargs as input and list as output.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(
        g, ["a", "b", "c", "d"], "g", input_as_kwargs=True, output_as_dict=False
    )
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(
        g,
        ["a", "b", "c", "d"],
        "e",
        "f",
        "g",
        input_as_kwargs=True,
        output_as_dict=False,
    )
    assert f1(a=1, b=2, c=3, d=4) == -9
    assert f2(a=1, b=2, c=3, d=4) == [3, 12, -9]


def test_wrap_with_function_input_as_args_output_as_dict():
    """
    Test wrapping a graph with a function, using args as input and dict as output.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(
        g, ["a", "b", "c", "d"], "g", input_as_kwargs=False, output_as_dict=True
    )
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(
        g,
        ["a", "b", "c", "d"],
        "e",
        "f",
        "g",
        input_as_kwargs=False,
        output_as_dict=True,
    )
    assert f1(1, 2, 3, 4) == -9
    assert f2(1, 2, 3, 4) == dict(e=3, f=12, g=-9)


def test_wrap_with_function_input_as_args_output_as_list():
    """
    Test wrapping a graph with a function, using args as input and list as output.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.wrap_graph_with_function(
        g, ["a", "b", "c", "d"], "g", input_as_kwargs=False, output_as_dict=False
    )
    # Get a function a,b,c,d -> [e,f,g]
    f2 = gr.wrap_graph_with_function(
        g,
        ["a", "b", "c", "d"],
        "e",
        "f",
        "g",
        input_as_kwargs=False,
        output_as_dict=False,
    )
    assert f1(1, 2, 3, 4) == -9
    assert f2(1, 2, 3, 4) == [3, 12, -9]


def test_lambdify():
    """
    Test lambdifying a graph.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.lambdify_graph(g, ["a", "b", "c", "d"], "g")
    assert f1(a=1, b=2, c=3, d=4) == -9


def test_lambdify_with_constants():
    """
    Test lambdifying a graph with some constants passed at the moment of lambdification.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")

    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)

    # Get a function a,b,c,d -> g
    f1 = gr.lambdify_graph(g, ["c", "d"], "g", {"a": 1, "b": 2})
    assert f1(c=3, d=4) == -9


def test_unfeasible_wrap():
    """
    Test that wrapping a graph with a function raises an error if the inputs are not sufficient to compute the outputs.
    """
    g = gr.Graph()
    gr.add_step(g, "d", "op_d", "a", "b", "c")
    g["op_d"] = lambda a, b, c: a + b + c
    gr.finalize_definition(g)

    with pytest.raises(ValueError):
        # Pass b as input, c as constant, but do not pass a
        f1 = gr.wrap_graph_with_function(
            g, ["b"], "d", constants={"c": 1}, input_as_kwargs=False
        )
    # Pass also a
    f2 = gr.wrap_graph_with_function(
        g, ["a", "b"], "d", constants={"c": 1}, input_as_kwargs=False
    )
    assert f2(1, 1) == 3


def test_get_execution_subgraph():
    """
    Test getting an execution subgraph from a graph with a conditional, and executing it.
    """
    g = gr.Graph()
    gr.add_step(g, "e", "op_e", "a", "b")
    gr.add_step(g, "f", "op_f", "c", "d")
    gr.add_step(g, "g", "op_g", "e", "f")
    gr.add_step(g, "h", "op_h", "e")
    gr.add_simple_conditional(g, "j", "i", "g", "h")
    gr.finalize_definition(g)
    operations = {
        "op_e": lambda x, y: x + y,
        "op_f": lambda x, y: x * y,
        "op_g": lambda x, y: x - y,
        "op_h": lambda x: x,
    }
    gr.set_internal_context(g, operations)
    gr.finalize_definition(g)
    context = {"e": 1, "f": 1, "i": True}

    h = gr.get_execution_subgraph(g, context, "j", "h")

    assert set(h.nodes) == {"j", "i", "g", "h", "op_h", "e", "op_g", "f"}

    res = gr.execute_graph_from_context(h, context, "j", "h")
    assert res["j"] == 0
    assert res["h"] == 1
