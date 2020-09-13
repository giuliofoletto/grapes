import threading
import graphviz

class GenericNode:
    def __init__(self, name):
        self.name = name
        self.mutex = threading.Lock()
        self.has_value = False
        self.value = None
        self.is_operation = False
        self.has_dependencies = False
        self.dependencies = []

class Placeholder(GenericNode):
    def __init__(self, name):
        super().__init__(name)

class Node(GenericNode):
    def __init__(self, name, func, *args, **kwargs):
        super().__init__(name)
        self.func = func
        self.arguments = args
        self.keyword_arguments = kwargs
        self.has_dependencies = True
        self.dependencies = [self.func] + list(self.arguments) + list(self.keyword_arguments.values())

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

    def clear_values(self):
        for key in self.nodes.keys():
            self.nodes[key].has_value = False

    def set_internal_state(self, dictionary):
        for key, value in dictionary.items():
            self.nodes[key].has_value = True
            self.nodes[key].value = value

    def get_internal_state(self):
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
        list_of_threads = []
        for dependency_name in node.dependencies:
            list_of_threads.append(threading.Thread(target = self.evaluate_target, args = (dependency_name,)))
        for t in list_of_threads:
            t.start()
        for t in list_of_threads:
            t.join()

        # Declare that the evaluation is going to start, wait if blocked
        node.mutex.acquire()
        # But check if it has already been computed in the meantime
        if node.has_value:
            node.mutex.release()
            return node.value
        # Actual computation happens here
        res = self.nodes[node.func].value(*self.get_list_of_values(node.arguments), **self.get_dict_of_values(node.keyword_arguments))
        # Save results and release
        node.value = res
        node.has_value = True
        node.mutex.release()
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

        # Declare that the evaluation is going to start, wait if blocked
        conditional.mutex.acquire()
        # But check if it has already been computed in the meantime
        if conditional.has_value:
            conditional.mutex.release()
            return conditional.value
        # Actual computation happens here
        res = self.evaluate_target(conditional.possibilities[index])
        # Save results and release
        conditional.value = res
        conditional.has_value = True
        conditional.mutex.release()
        return conditional.value

    def execute_to_targets(self, *targets):
        list_of_threads = []
        for target in targets:
            list_of_threads.append(threading.Thread(target = self.evaluate_target, args = (target,)))
        for t in list_of_threads:
            t.start()
        for t in list_of_threads:
            t.join()

    def get_graphviz_digraph(self, name = None, directory = "visualizations", hide_operations = False, **attrs):
        if name is None:
            name = self.name
        g = graphviz.Digraph(name = name, directory = directory)
        g.attr(**attrs)
        for name, node in self.nodes.items():
            attributes = {}
            if node.is_operation and hide_operations:
                continue
            elif node.is_operation:
                attributes.update({"shape": "ellipse"})
            elif isinstance(node, SimpleConditional):
                attributes.update({"shape": "diamond"})
            else:
                attributes.update({"shape": "box"})
            if node.has_value:
                attributes.update({"style": "filled", "fillcolor": "darkolivegreen1"})    
            g.node(name, **attributes)
        for name, node in self.nodes.items():
            special_dependencies = []
            if isinstance(node, Node):
                if not hide_operations:
                    g.edge(node.func, name, arrowhead = "dot")
                special_dependencies.append(node.func)
            elif isinstance(node, SimpleConditional):
                for condition in node.conditions:
                    g.edge(condition, name, arrowhead = "diamond")
                special_dependencies.extend(node.conditions)    
            for dependency_name in [x for x in node.dependencies if x not in special_dependencies]:
                g.edge(dependency_name, name)
        return g