class GenericNode:
    def __init__(self, name):
        self.name = name
        self.has_value = False
        self.value = None
        self.is_operation = False
        self.has_dependencies = False
        self.dependencies = []

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def isCompatible(self, other):
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
        if not self.isCompatible(other):
            raise ValueError("Cannot merge node with something incompatible with it")
        if self == other:
            return # Nothing to do in this case
        if not self.has_value and other.has_value:
            self.value = other_value
            self.has_value = True
        if not self.has_dependencies and other.has_dependencies:
            self.dependencies = other.dependencies
            self.has_dependencies = True
        self.is_operation = self.is_operation or other.is_operation

class Placeholder(GenericNode):
    def __init__(self, name):
        super().__init__(name)

    def merge(self, other):
        super().merge(other)
        # A Placeholder likes to be replaced
        self.__class__ = other.__class__
        self.__dict__ = other.__dict__

class Node(GenericNode):
    def __init__(self, name, func, *args, **kwargs):
        super().__init__(name)
        self.func = func
        self.arguments = args
        self.keyword_arguments = kwargs
        self.has_dependencies = True
        self.dependencies = [self.func] + list(self.arguments) + list(self.keyword_arguments.values())

    def merge(self, other):
        super().merge(other)
        if self == other:
            return # Nothing to do in this case, it must be done again after doing it in super
        if type(other) == type(self):
            if self.func is None and other.func is not None:
                self.func = other.func
            self.arguments = self.arguments + other.arguments
            self.keyword_arguments.update(other.keyword_arguments)

class SimpleConditional(GenericNode):
    def __init__(self, name, condition, value_true, value_false):
        super().__init__(name)
        self.conditions = [condition]
        self.possibilities = [value_true, value_false]
        self.has_dependencies = True
        self.dependencies = [condition, value_true, value_false]

class Graph:
    def __init__(self, name = "Graph"):
        self.name = name
        self.nodes = {}

    def __getitem__(self, key):
        return self.nodes[key].value

    def __setitem__(self, key, value):
        self.nodes[key].value = value
        self.nodes[key].has_value = True

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

    def add_placeholder(self, name):
        placeholder = Placeholder(name)
        self.nodes.update({name: placeholder})

    def add_node(self, name, func = None, *args, **kwargs):
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
        # We simplify insertion by taking care of undefined dependencies as placeholders
        for dependency_name in [condition, value_true, value_false]:
            if dependency_name not in self.nodes:
                self.add_placeholder(dependency_name)

        # Here the actual insertion happens
        conditional = SimpleConditional(name, condition, value_true, value_false)
        self.nodes.update({name: conditional})

    def clear_values(self, keep_operations = False):
        for key, node in self.nodes.items():
            if keep_operations and node.is_operation:
                continue
            self.nodes[key].has_value = False

    def set_internal_state(self, dictionary):
        for key, value in dictionary.items():
            # Accept dictionaries with more keys than needed
            if key in self.nodes:
                self.nodes[key].has_value = True
                self.nodes[key].value = value

    def get_internal_state(self, only_data = False):
        if only_data:
            return {key : self.nodes[key].value for key, value in self.nodes.items() if (self.nodes[key].has_value and not self.nodes[key].is_operation)}
        else:
            return {key : self.nodes[key].value for key, value in self.nodes.items() if self.nodes[key].has_value}

    def get_list_of_values(self, list_of_keys):
        res = []
        for key in list_of_keys:
            res.append(self.nodes[key].value)
        return res
    
    def get_dict_of_values(self, dictionary):
        return {key : self.nodes[value].value for key, value in dictionary.items()}

    def evaluate_target(self, target):
        node = self.nodes[target]
        if isinstance(node, Node) or isinstance(node, Placeholder):
            return self.evaluate_node(node)
        elif isinstance(node, SimpleConditional):
            return self.evaluate_conditional(node)

    def evaluate_node(self, node):
        # Check if it already has a value
        if node.has_value:
            return node.value
        # If not, evaluate all arguments
        for dependency_name in node.dependencies:
            self.evaluate_target(dependency_name)

        # Actual computation happens here
        res = self.nodes[node.func].value(*self.get_list_of_values(node.arguments), **self.get_dict_of_values(node.keyword_arguments))
        # Save results and release
        node.value = res
        node.has_value = True
        return node.value

    def evaluate_conditional(self, conditional):
        # Check if it already has a value
        if conditional.has_value:
            return conditional.value
        # If not, evaluate the conditions until one is found true
        for index, condition in enumerate(conditional.conditions):
            res = self.evaluate_target(condition)
            if res:
                break
        else: # Happens if loop is never broken, i.e. when no conditions are true
            index = -1

        # Actual computation happens here
        res = self.evaluate_target(conditional.possibilities[index])
        # Save results and release
        conditional.value = res
        conditional.has_value = True
        return conditional.value

    def execute_to_targets(self, *targets):
        list_of_threads = []
        for target in targets:
            self.evaluate_target(target)

    def isCompatible(self, other):
        """Check if self and other can be merged. Currently DAG status is not verified"""
        if not isinstance(other, Graph):
            return False
        common_nodes = self.nodes.keys() & other.nodes.keys() # Intersection
        for key in common_nodes:
            if not self.nodes[key].isCompatible(other.nodes[key]):
                return False
        return True

    def merge(self, other):
        if not self.isCompatible(other):
            raise ValueError("Cannot merge incompatible graphs")
        common_nodes = self.nodes.keys() & other.nodes.keys() # Intersection
        for key in common_nodes:
            self.nodes[key].merge(other.nodes[key])
        new_nodes = {k : other.nodes[k] for k in other.nodes.keys() - self.nodes.keys()}
        self.nodes.update(new_nodes)
