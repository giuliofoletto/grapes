"""
Some tools to compose functions into one.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

import inspect


def identity_token():
    """
    A trivial token that has the only purpose of being identifiable
    """
    pass


def function_compose(
    func,
    subfuncs,
    func_dependencies,
    subfuncs_dependencies,
    func_signature,
    subfuncs_signatures,
):
    """
    Compose functions.

    Parameters
    ----------
    func : callable
        External function
    subfuncs : list of callables
        List of internal functions to be composed with func. If identity_token is passed here, it is replaced by the value of the argument.
    func_dependencies : list of hashables
        Names of the arguments of func (usually they should correspond to node names in a graph)
    subfuncs_dependencies : list of lists of hashables
        Names of the arguments that are passed to the subfuncs when calling the new function (usually they should correspond to node names in a graph)
    func_signature : list of hashables
        Names of the arguments of the old func
    subfuncs_signatures : list of lists of hashables
        Names of the arguments of the old subfuncs
    """
    return lambda **kwargs: func(
        **{
            func_signature[i]: (
                subfuncs[i](
                    **{
                        signature_name: kwargs[dependency_name]
                        for signature_name, dependency_name in zip(
                            subfuncs_signatures[i], subfuncs_dependencies[i]
                        )
                    }
                )
                if subfuncs[i] is not identity_token
                else kwargs[func_dependencies[i]]
            )
            for i in range(len(subfuncs))
        }
    )


def function_compose_simple(
    func,
    subfuncs,
    func_dependencies,
    subfuncs_dependencies,
    func_signature=None,
    subfuncs_signatures=None,
):
    """
    Compose functions, without the need to pass signatures, as they are found automatically.

    Parameters
    ----------
    func : callable
        External function
    subfuncs : list of callables
        List of internal functions to be composed with func
    func_dependencies : list of hashables
        Names of the arguments of the new function (usually they should correspond to node names in a graph)
    subfuncs_dependencies : list of lists of hashables
        Names of the arguments that are passed to the subfuncs when calling the new function (usually they should correspond to node names in a graph)
    func_signature : list of hashables
        Names of the arguments of the old func
    subfuncs_signatures : list of lists of hashables
        Names of the arguments of the old subfuncs
    """
    if func_signature is None:
        if inspect.getfullargspec(func).varargs is not None:
            raise ValueError(
                "Functions with varargs are not supported by Function Composer"
            )
        elif (
            inspect.getfullargspec(func).varargs is None
            and inspect.getfullargspec(func).varkw is None
        ):  # Well defined spec
            func_signature = list(inspect.signature(func).parameters.keys())
        else:
            func_signature = func_dependencies
    if subfuncs_signatures is None:
        subfuncs_signatures = []
        for index, subfunc in enumerate(subfuncs):
            if inspect.getfullargspec(func).varargs is not None:
                raise ValueError(
                    "Functions with varargs are not supported by Function Composer"
                )
            elif (
                inspect.getfullargspec(subfunc).varargs is None
                and inspect.getfullargspec(subfunc).varkw is None
            ):  # Well defined spec
                this_signature = list(inspect.signature(subfunc).parameters.keys())
            else:
                this_signature = subfuncs_dependencies[index]
            subfuncs_signatures.append(this_signature)
    return function_compose(
        func,
        subfuncs,
        func_dependencies,
        subfuncs_dependencies,
        func_signature,
        subfuncs_signatures,
    )
