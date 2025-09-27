"""
This module contains tests of function composer.
"""

import pytest
import grapes as gr


def test_one_argument():
    """
    Test composing two functions with one argument each.
    """

    def external(argument):
        return 3 * argument

    def internal(argument_of_internal):
        return 2 * argument_of_internal

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[internal],
        func_dependencies=["argument"],
        subfuncs_dependencies=[["argument_of_internal"]],
    )

    assert composed(argument_of_internal=1) == 6


def test_change_names():
    """
    Test changing argument name for external and internal functions
    """

    def external(argument):
        return 3 * argument

    def internal(argument_of_internal):
        return 2 * argument_of_internal

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[internal],
        func_dependencies=["new_argument"],
        subfuncs_dependencies=[["new_argument_of_internal"]],
        func_signature=["argument"],
        subfuncs_signatures=[["argument_of_internal"]],
    )

    assert composed(new_argument_of_internal=1) == 6


def test_two_arguments():
    """
    Test composing two functions with one argument each into a function with two arguments.
    """

    def external(first_argument, second_argument):
        return first_argument + second_argument

    def first_function(argument_of_first_function):
        return 2 * argument_of_first_function

    def second_function(argument_of_second_function):
        return 3 * argument_of_second_function

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[first_function, second_function],
        func_dependencies=["first_argument", "second_argument"],
        subfuncs_dependencies=[
            ["argument_of_first_function"],
            ["argument_of_second_function"],
        ],
    )

    assert composed(argument_of_first_function=1, argument_of_second_function=1) == 5


def test_two_arguments_compose_first():
    """
    Test composing a function of an argument into a function with two arguments, replacing the first argument.
    """

    def external(first_argument, second_argument):
        return first_argument + second_argument

    def first_function(argument_of_first_function):
        return 2 * argument_of_first_function

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[first_function, gr.function_composer.identity_token],
        func_dependencies=["first_argument", "second_argument"],
        subfuncs_dependencies=[["argument_of_first_function"]],
    )

    assert composed(argument_of_first_function=1, second_argument=1) == 3


def test_two_arguments_compose_second():
    """
    Test composing a function of an argument into a function with two arguments, replacing the second argument.
    """

    def external(first_argument, second_argument):
        return first_argument + second_argument

    def second_function(argument_of_second_function):
        return 2 * argument_of_second_function

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[gr.function_composer.identity_token, second_function],
        func_dependencies=["first_argument", "second_argument"],
        subfuncs_dependencies=[[], ["argument_of_second_function"]],
    )  # Need to pass something to keep indexes aligned

    assert composed(first_argument=1, argument_of_second_function=1) == 3


def test_keyword_argument():
    """
    Test composing a function with a keyword argument.
    """

    def external(first_argument, *, one_keyword_argument):
        return first_argument + one_keyword_argument

    def first_function(argument_of_first_function):
        return 2 * argument_of_first_function

    def keyword_function(argument_of_keyword_function):
        return 3 * argument_of_keyword_function

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[first_function, keyword_function],
        func_dependencies=["first_argument", "one_keyword_argument"],
        subfuncs_dependencies=[
            ["argument_of_first_function"],
            ["argument_of_keyword_function"],
        ],
    )

    assert composed(argument_of_first_function=1, argument_of_keyword_function=1) == 5


def test_kwargs():
    """
    Test composing a function with varkwargs.
    """

    def external(**kwargs):
        values = kwargs.values()
        return sum(values)

    def first_function(argument_of_first_function):
        return 2 * argument_of_first_function

    def second_function(argument_of_second_function):
        return 3 * argument_of_second_function

    composed = gr.function_composer.function_compose_simple(
        func=external,
        subfuncs=[first_function, second_function],
        func_dependencies=["first_argument", "second_argument"],
        subfuncs_dependencies=[
            ["argument_of_first_function"],
            ["argument_of_second_function"],
        ],
    )

    assert composed(argument_of_first_function=1, argument_of_second_function=1) == 5
