import graphviz
from .. import *

def get_graphviz_digraph(graph, name = None, directory = "visualizations", hide_operations = False, pretty_names = False, include_values = False, **attrs):
    if name is None:
        name = graph.name
    g = graphviz.Digraph(name = name, directory = directory)
    g.attr(**attrs)
    for name, node in graph.nodes.items():
        label = prettify_label(name) if pretty_names else name
        if include_values and node.has_value:
            if isinstance(node.value, float):
                value_in_label = "{:.2e}".format(node.value)
            else:
                value_in_label = str(node.value)
            label += "\n" + value_in_label.partition('\n')[0]
            if value_in_label.find("\n") != -1:
                label += "\n..."
        attributes = {"label": label} if label != name else {}
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

def prettify_label(name):
    return "".join(c.upper() if ((i > 0 and name[i-1] == "_") or i == 0) else c for i, c in enumerate(name)).replace("_", " ")