import threading
import graphviz

class Node:
    def __init__(self, name, func = None, *args, **kwargs):
        self.name = name
        self.func = func
        self.arguments = args
        self.keyword_arguments = kwargs
        if self.func == None:
            self.is_placeholder = True
        else:
            self.is_placeholder = False
        self.is_operation = False
        self.mutex = threading.Lock()
        self.has_value = False
        self.value = None

class Graph:
    def __init__(self, name = "Graph"):
        self.name = name
        self.nodes = {}

    def __getitem__(self, key):
        return self.nodes[key].value

    def __setitem__(self, key, value):
        self.nodes[key].value = value
        self.nodes[key].has_value = True

    def add_node(self, name, func = None, *args, **kwargs):
        # We simplify insertion by taking care of undefined dependencies as placeholders
        dependencies = []
        if func is not None:
            dependencies.append(func)
        dependencies.extend(args)
        dependencies.extend(list(kwargs.values()))
        for dependency_name in dependencies:
            if dependency_name not in self.nodes:
                self.add_node(dependency_name)

        # Here the actual insertion happens
        node = Node(name, func, *args, **kwargs)
        self.nodes.update({name: node})

        # Mark as operation what is used as such
        if func is not None:
            self.nodes[func].is_operation = True

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

    def evaluate_node(self, target):
        # Check if it already has a value
        node = self.nodes[target]
        if node.has_value:
            return
        # If not, evaluate all arguments
        list_of_threads = []
        for argument in node.arguments:
            list_of_threads.append(threading.Thread(target = self.evaluate_node, args = (argument,)))
        for _, value in node.keyword_arguments.items():
            list_of_threads.append(threading.Thread(target = self.evaluate_node, args = (value,)))
        for t in list_of_threads:
            t.start()
        for t in list_of_threads:
            t.join()

        # Declare that the evaluation is going to start, wait if blocked
        node.mutex.acquire()
        # But check if it has already been computed in the meantime
        if node.has_value:
            node.mutex.release()
            return
        # Actual computation happens here
        res = self.nodes[node.func].value(*self.get_list_of_values(node.arguments), **self.get_dict_of_values(node.keyword_arguments))
        # Save results and release
        node.value = res
        node.has_value = True
        node.mutex.release()
        return

    def execute_to_targets(self, *targets):
        list_of_threads = []
        for target in targets:
            list_of_threads.append(threading.Thread(target = self.evaluate_node, args = (target,)))
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
            else:
                attributes.update({"shape": "box"})
            if node.has_value:
                attributes.update({"style": "filled", "fillcolor": "darkolivegreen1"})    
            g.node(name, **attributes)
        for name, node in self.nodes.items():
            if node.func is not None and not hide_operations:
                g.edge(node.func, name, arrowhead = "dot")
            for argument in node.arguments:
                g.edge(argument, name)
            for argument in list(node.keyword_arguments.values()):
                g.edge(argument, name)
        return g