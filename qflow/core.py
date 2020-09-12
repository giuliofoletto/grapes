import threading

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
        self.mutex = threading.Lock()
        self.has_value = False
        self.value = None

class Graph:
    def __init__(self):
        self.nodes = {}

    def __getitem__(self, key):
        return self.nodes[key].value

    def __setitem__(self, key, value):
        self.nodes[key].value = value
        self.nodes[key].has_value = True

    def add_node(self, node):
        self.nodes.update({node.name: node})

    def clear_values(self):
        for key in self.nodes.keys():
            self.nodes[key].has_value = False

    def set_internal_state(self, dictionary):
        for key, value in dictionary.items():
            self.nodes[key].has_value = True
            self.nodes[key].value = value

    def get_internal_state(self):
        return {key : self.nodes[key].value for key, value in self.nodes.items() if self.nodes[key].has_value}