"""
Core of the qflow package. Includes the classes for nodes and graphs.

Author: Giulio Foletto. 
"""
from . import function_composer


class GenericNode:
    """
    Generic class for all kinds of nodes.
    """

    def __init__(self, name):
        """
        Constructor. Nodes are created with just a name, values are provided by the graph.
        """
        self.name = name
        self.has_value = False
        self.value = None
        self.is_operation = False
        self.has_dependencies = False
        self.dependencies = []

    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def isCompatible(self, other):
        """
        Check if a node is compatible to another, meaning that they can replace each other in a graph.
        """
        # If other is not a GenericNode, return False
        if not isinstance(other, GenericNode):
            return False
        # If they are equal, return True
        if self == other:
            return True
        # If they are not named the same, return False
        if self.name != other.name:
            return False
        # If they both have values but they differ, return False. If only one has a value, proceed
        if self.has_value and other.has_value and self.value != other.value:
            return False
        # If they both have dependencies but they differ, return False. If only one has dependencies, proceed
        if self.has_dependencies and other.has_dependencies and self.dependencies != other.dependencies:
            return False
        # Return True if they have the same name, at least one has no dependencies (or they are the same), at least one has no value (or they are the same)
        return True

    def merge(self, other):
        """
        Merge other into self.
        """
        if not self.isCompatible(other):
            raise ValueError("Cannot merge node with something incompatible with it")
        if self == other:
            return  # Nothing to do in this case
        if not self.has_value and other.has_value:
            self.value = other_value
            self.has_value = True
        if not self.has_dependencies and other.has_dependencies:
            self.dependencies = other.dependencies
            self.has_dependencies = True
        self.is_operation = self.is_operation or other.is_operation


class Placeholder(GenericNode):
    """
    A trivial node with no children.
    """

    def __init__(self, name):
        super().__init__(name)

    def merge(self, other):
        super().merge(other)
        # A Placeholder likes to be replaced
        self.__class__ = other.__class__
        self.__dict__ = other.__dict__


class Node(GenericNode):
    """
    The most typical kind of node. It has a special parent that takes the role of an operation, the recipe used to evaluate the node.
    """

    def __init__(self, name, func, *args, **kwargs):
        """
        Constructor.

        Parameters
        ----------
        name: hashable (typically string)
            Name of the node, which identifies it in the graph.
        func: hashable (typically string)
            Name of the parent node that takes the role of the recipe used to evaluate this node.
        args: list of hashables
            Names of other parent nodes that will be passed to func as arguments.
        kwargs: dict of hashables
            Key, value pairs that will be passed to func as keyword arguments. Keys are keywords of the func, values are names of nodes.
        """
        super().__init__(name)
        self.func = func
        self.arguments = args
        self.keyword_arguments = kwargs
        self.has_dependencies = True
        self.dependencies = [self.func] + list(self.arguments) + list(self.keyword_arguments.values())

    def merge(self, other):
        """
        Merge two nodes.
        """
        super().merge(other)
        if self == other:
            return  # Nothing to do in this case, it must be done again after doing it in super
        if type(other) == type(self):
            if self.func is None and other.func is not None:
                self.func = other.func
            self.arguments = self.arguments + other.arguments
            self.keyword_arguments.update(other.keyword_arguments)


class SimpleConditional(GenericNode):
    """
    A node that takes one of two values (taken from parent nodes) based on the value of another node.
    """

    def __init__(self, name, condition, value_true, value_false):
        """
        Constructor.

        Parameters
        ----------
        name: hashable
            Name of the node.
        condition: hashable
            Name of the parent nodes that acts as a condition
        value_true: hashable
            Name of the parent node that will give its value to this node if condition is True
        value_false: hashable
            Name of the parent node that will give its value to this node if condition is False
        """
        super().__init__(name)
        self.conditions = [condition]
        self.possibilities = [value_true, value_false]
        self.has_dependencies = True
        self.dependencies = [condition, value_true, value_false]


class Graph:
    """
    Class that represents a graph of nodes.
    """

    def __init__(self, name="Graph"):
        """
        Constructor.

        Parameters
        ----------
        name: hashable
            Name of the graph.
        """
        self.name = name
        self.nodes = {}

    def __getitem__(self, key):
        """
        Get the value of a node with []
        """
        return self.nodes[key].value

    def __setitem__(self, key, value):
        """
        Set the value of a node with []
        """
        self.nodes[key].value = value
        self.nodes[key].has_value = True

    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def add_placeholder(self, name):
        """
        Interface to add a placeholder node to the graph.
        """
        placeholder = Placeholder(name)
        self.nodes.update({name: placeholder})

    def add_node(self, name, func=None, *args, **kwargs):
        """
        Interface to add a node to the graph.
        """
        # We simplify insertion by taking care of undefined dependencies as placeholders
        dependencies = []
        if func is not None:
            dependencies.append(func)
        dependencies.extend(args)
        dependencies.extend(list(kwargs.values()))
        for dependency_name in dependencies:
            if dependency_name not in self.nodes:
                self.add_placeholder(dependency_name)

        # Here the actual insertion happens
        node = Node(name, func, *args, **kwargs)
        self.nodes.update({name: node})

        # Mark as operation what is used as such
        if func is not None:
            self.nodes[func].is_operation = True

    def add_simple_conditional(self, name, condition, value_true, value_false):
        """
        Interface to add a conditional to the graph.
        """
        # We simplify insertion by taking care of undefined dependencies as placeholders
        for dependency_name in [condition, value_true, value_false]:
            if dependency_name not in self.nodes:
                self.add_placeholder(dependency_name)

        # Here the actual insertion happens
        conditional = SimpleConditional(name, condition, value_true, value_false)
        self.nodes.update({name: conditional})

    def clear_values(self, keep_operations=False):
        """
        Clear all values in the graph nodes.

        Parameters
        ----------
        keep_operations: bool
            Whether to spare operations from clearing.
        """
        for key, node in self.nodes.items():
            if keep_operations and node.is_operation:
                continue
            self.nodes[key].has_value = False

    def update_internal_context(self, dictionary):
        """
        Update internal context with a dictionary.
        """
        for key, value in dictionary.items():
            # Accept dictionaries with more keys than needed
            if key in self.nodes:
                self.nodes[key].has_value = True
                self.nodes[key].value = value

    def set_internal_context(self, dictionary, keep_operations=False):
        """
        Clear all values and then set a new internal context with a dictionary.

        Parameters
        ----------
        keep_operations: bool
            Whether to spare operations from clearing.
        """
        self.clear_values(keep_operations)
        self.update_internal_context(dictionary)

    def get_internal_context(self, only_data=False):
        """
        Get the internal context.

        Parameters
        ----------
        only_data: bool
            Whether to return only data or also operations.
        """
        if only_data:
            return {key: self.nodes[key].value for key, value in self.nodes.items() if (self.nodes[key].has_value and not self.nodes[key].is_operation)}
        else:
            return {key: self.nodes[key].value for key, value in self.nodes.items() if self.nodes[key].has_value}

    def get_list_of_values(self, list_of_keys):
        """
        Get values as list.

        Parameters
        ----------
        list_of_keys: list of hashables (typically strings)
            List of names of nodes whose values are required

        Returns
        -------
        list
            List like list_of_keys which contains values of nodes
        """
        res = []
        for key in list_of_keys:
            res.append(self.nodes[key].value)
        return res

    def get_dict_of_values(self, list_of_keys):
        """
        Get values as dictionary.

        Parameters
        ----------
        list_of_keys: list of hashables (typically strings)
            List of names of nodes whose values are required

        Returns
        -------
        dict
            Dictionary whose keys are the elements of list_of_keys and whose values are the corresponding node values
        """
        return {key: self.nodes[key].value for key in list_of_keys}

    def get_kwargs_values(self, dictionary):
        """
        Get values from the graph, using a dictionary that works like function kwargs.

        Parameters
        ----------
        dictionary: dict
            Keys in dictionary are to be interpreted as keys for function kwargs, while values in dictionary are node names

        Returns
        -------
        dict
            A dict with the same keys of the input dictionary, but with values replaced by the values of the nodes
        """
        return {key: self.nodes[value].value for key, value in dictionary.items()}

    def evaluate_target(self, target):
        """
        Generic interface to evaluate a GenericNode.
        """
        node = self.nodes[target]
        if isinstance(node, Node) or isinstance(node, Placeholder):
            return self.evaluate_node(node)
        elif isinstance(node, SimpleConditional):
            return self.evaluate_conditional(node)

    def evaluate_node(self, node):
        """
        Evaluate of a node.
        """
        # Check if it already has a value
        if node.has_value:
            return node.value
        # If not, evaluate all arguments
        for dependency_name in node.dependencies:
            self.evaluate_target(dependency_name)

        # Actual computation happens here
        try:
            res = self.nodes[node.func].value(*self.get_list_of_values(node.arguments), **self.get_kwargs_values(node.keyword_arguments))
        except Exception as e:
            if len(e.args) > 0:
                e.args = ("While evaluating " + node.name + ": " + e.args[0],) + e.args[1:]
            raise
        # Save results and release
        node.value = res
        node.has_value = True
        return node.value

    def evaluate_conditional(self, conditional):
        """
        Evaluate a conditional.
        """
        # Check if it already has a value
        if conditional.has_value:
            return conditional.value
        # If not, evaluate the conditions until one is found true
        for index, condition in enumerate(conditional.conditions):
            res = self.evaluate_target(condition)
            if res:
                break
        else:  # Happens if loop is never broken, i.e. when no conditions are true
            index = -1

        # Actual computation happens here
        res = self.evaluate_target(conditional.possibilities[index])
        # Save results and release
        conditional.value = res
        conditional.has_value = True
        return conditional.value

    def execute_to_targets(self, *targets):
        """
        Evaluate all nodes in the graph that are needed to reach the targets.
        """
        list_of_threads = []
        for target in targets:
            self.evaluate_target(target)

    def isCompatible(self, other):
        """
        Check if self and other can be merged. Currently DAG status is not verified.
        """
        if not isinstance(other, Graph):
            return False
        common_nodes = self.nodes.keys() & other.nodes.keys()  # Intersection
        for key in common_nodes:
            if not self.nodes[key].isCompatible(other.nodes[key]):
                return False
        return True

    def merge(self, other):
        """
        Merge other into self.
        """
        if not self.isCompatible(other):
            raise ValueError("Cannot merge incompatible graphs")
        common_nodes = self.nodes.keys() & other.nodes.keys()  # Intersection
        for key in common_nodes:
            self.nodes[key].merge(other.nodes[key])
        new_nodes = {k: other.nodes[k] for k in other.nodes.keys() - self.nodes.keys()}
        self.nodes.update(new_nodes)

    def simplify_dependency(self, node_name, dependency_name):
        node = self.nodes[node_name]
        # Make everything a keyword argument. This is the fate of a simplified node
        node.keyword_arguments.update({argument: argument for argument in node.arguments})
        # Build lists of dependencies
        func_dependencies = node.dependencies[1:]
        subfuncs = []
        subfuncs_dependencies = []
        for argument in node.keyword_arguments:
            if argument == dependency_name:
                subfuncs.append(self[self.nodes[dependency_name].func])
                subfuncs_dependencies.append(self.nodes[dependency_name].dependencies[1:])
            else:
                subfuncs.append(function_composer.identity_token)
                subfuncs_dependencies.append([argument])
        # Compose the functions
        self[node.func] = function_composer.function_compose_simple(self[node.func], subfuncs, func_dependencies, subfuncs_dependencies)
        # Update node
        node.arguments = []
        node.keyword_arguments.update({argument: argument for argument in self.nodes[dependency_name].dependencies[1:]})
        node.keyword_arguments = {key: value for key, value in node.keyword_arguments.items() if value != dependency_name}
        node.dependencies = [node.func] + list(node.arguments) + list(node.keyword_arguments.values())
        self.nodes[node_name] = node

    def simplify_all_dependencies(self, node_name, exclude=[]):
        dependencies = self.nodes[node_name].dependencies[1:]
        for dependency in dependencies:
            if dependency not in exclude and isinstance(self.nodes[dependency], Node):
                self.simplify_dependency(node_name, dependency)
