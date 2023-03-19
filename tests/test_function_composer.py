"""
Tests of function composer.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import pytest
import grapes as gr


def test_one_argument():
    def external(argument):
        return 3*argument

    def internal(argument_of_internal):
        return 2*argument_of_internal

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[internal],
                                                            func_dependencies=["argument"],
                                                            subfuncs_dependencies=[["argument_of_internal"]])

    assert composed(argument_of_internal=1) == 6


def test_change_names():
    """
    Change argument name for external and internal functions
    """
    def external(argument):
        return 3*argument

    def internal(argument_of_internal):
        return 2*argument_of_internal

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[internal],
                                                            func_dependencies=["new_argument"],
                                                            subfuncs_dependencies=[["new_argument_of_internal"]],
                                                            func_signature=["argument"],
                                                            subfuncs_signatures=[["argument_of_internal"]])

    assert composed(new_argument_of_internal=1) == 6


def test_two_arguments():
    def external(first_argument, second_argument):
        return first_argument + second_argument

    def first_function(argument_of_first_function):
        return 2*argument_of_first_function

    def second_function(argument_of_second_function):
        return 3*argument_of_second_function

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[first_function, second_function],
                                                            func_dependencies=["first_argument", "second_argument"],
                                                            subfuncs_dependencies=[["argument_of_first_function"], ["argument_of_second_function"]])

    assert composed(argument_of_first_function=1, argument_of_second_function=1) == 5


def test_two_arguments_compose_first():
    def external(first_argument, second_argument):
        return first_argument + second_argument

    def first_function(argument_of_first_function):
        return 2*argument_of_first_function

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[first_function, gr.function_composer.identity_token],
                                                            func_dependencies=["first_argument", "second_argument"],
                                                            subfuncs_dependencies=[["argument_of_first_function"]])

    assert composed(argument_of_first_function=1, second_argument=1) == 3


def test_two_arguments_compose_second():
    def external(first_argument, second_argument):
        return first_argument + second_argument

    def second_function(argument_of_second_function):
        return 2*argument_of_second_function

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[gr.function_composer.identity_token, second_function],
                                                            func_dependencies=["first_argument", "second_argument"],
                                                            subfuncs_dependencies=[[], ["argument_of_second_function"]])  # Need to pass something to keep indexes aligned

    assert composed(first_argument=1, argument_of_second_function=1) == 3


def test_keyword_argument():
    def external(first_argument, *,  one_keyword_argument):
        return first_argument + one_keyword_argument

    def first_function(argument_of_first_function):
        return 2*argument_of_first_function

    def keyword_function(argument_of_keyword_function):
        return 3*argument_of_keyword_function

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[first_function, keyword_function],
                                                            func_dependencies=["first_argument", "one_keyword_argument"],
                                                            subfuncs_dependencies=[["argument_of_first_function"], ["argument_of_keyword_function"]])

    assert composed(argument_of_first_function=1, argument_of_keyword_function=1) == 5


def test_kwargs():
    def external(**kwargs):
        values = kwargs.values()
        return sum(values)

    def first_function(argument_of_first_function):
        return 2*argument_of_first_function

    def second_function(argument_of_second_function):
        return 3*argument_of_second_function

    composed = gr.function_composer.function_compose_simple(func=external,
                                                            subfuncs=[first_function, second_function],
                                                            func_dependencies=["first_argument", "second_argument"],
                                                            subfuncs_dependencies=[["argument_of_first_function"], ["argument_of_second_function"]])

    assert composed(argument_of_first_function=1, argument_of_second_function=1) == 5
