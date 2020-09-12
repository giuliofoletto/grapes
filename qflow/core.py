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
        self.is_computed = False
        self.value = None