import graphviz
from .. import *

def get_graphviz_digraph(graph, name = None, directory = "visualizations", hide_operations = False, **attrs):
    if name is None:
        name = graph.name
    g = graphviz.Digraph(name = name, directory = directory)
    g.attr(**attrs)
    for name, node in graph.nodes.items():
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
    for name, node in graph.nodes.items():
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