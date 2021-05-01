"""
Core of the qflow package. Includes the classes for nodes and graphs.

Author: Giulio Foletto. 
"""
import networkx as nx
from . import function_composer


starting_node_properties = {"type": "standard", "has_value": False, "value": None, "is_frozen": False, "is_recipe": False}


class Graph():
    """
    Class that represents a graph of nodes.
    """

    def __init__(self, nx_digraph=None):
        # Internally, we handle a nx_digraph
        if nx_digraph == None:
            self._nxdg = nx.DiGraph()
        else:
            self._nxdg = nx_digraph
        # Alias for easy access
        self.nodes = self._nxdg.nodes

    def __getitem__(self, node):
        """
        Get the value of a node with []
        """
        return self.nodes[node]["value"]

    def __setitem__(self, node, value):
        """
        Set the value of a node with []
        """
        self.nodes[node]["value"] = value
        self.nodes[node]["has_value"] = True

    def __eq__(self, other):
        """
        Equality check based on all members.
        """
        return (isinstance(other, self.__class__) and nx.is_isomorphic(self._nxdg, other._nxdg, dict.__eq__, dict.__eq__))

    def add_step(self, name, recipe=None, *args, **kwargs):
        """
        Interface to add a node to the graph, with all its dependencies.
        """
        # Check that if a node has dependencies, it also has a recipe
        if recipe is None and (len(args) > 0 or len(kwargs.keys()) > 0):
            raise ValueError("Cannot add node with dependencies without a recipe")

        elif recipe is None:  # Accept nodes with no dependencies
            self._nxdg.add_node(name, **starting_node_properties)

        else:  # Standard case
            # Add the node
            self._nxdg.add_node(name, recipe=recipe, args=args, kwargs=kwargs, **starting_node_properties)

            # Add and connect the recipe
            self._nxdg.add_node(recipe, **starting_node_properties)
            self.nodes[recipe]["is_recipe"] = True
            # Note: adding argument to the edges is elegant but impractical.
            # If relations were defined through edges attributes rather than stored inside nodes,
            # retrieving them would require iterating through all edges and selecting the ones with the right attributes.
            # Although feasible, this is much slower than simply accessing node attributes.
            self._nxdg.add_edge(recipe, name)

            # Add and connect the other dependencies
            for arg in args:
                # Avoid adding existing dependencies so as not to overwrite attributes
                if arg not in self.nodes:
                    self._nxdg.add_node(arg, **starting_node_properties)
                self._nxdg.add_edge(arg, name)
            for value in kwargs.values():
                # Avoid adding existing dependencies so as not to overwrite attributes
                if value not in self.nodes:
                    self._nxdg.add_node(value, **starting_node_properties)
                self._nxdg.add_edge(value, name)

    def add_simple_conditional(self, name, condition, value_true, value_false):
        """
        Interface to add a conditional to the graph.
        """
        # Add all nodes
        self._nxdg.add_node(name, **starting_node_properties)
        for node in [condition, value_true, value_false]:
            # Avoid adding existing dependencies so as not to overwrite attributes
            if node not in self.nodes:
                self._nxdg.add_node(node, **starting_node_properties)

        # Connect edges
        self._nxdg.add_edge(condition, name)
        self._nxdg.add_edge(value_true, name)
        self._nxdg.add_edge(value_false, name)

        # Specify that this node is a conditional
        self.nodes[name]["type"] = "conditional"

        # Add conditions name to the list of conditions of the conditional
        self.nodes[name]["conditions"] = [condition]

        # Add possibilities to the list of possibilities of the conditional
        self.nodes[name]["possibilities"] = [value_true, value_false]

    def is_recipe(self, node):
        return self.nodes[node]["is_recipe"]

    def get_recipe(self, node):
        attributes = self.nodes[node]
        if "recipe" in attributes and attributes["recipe"] is not None:
            return attributes["recipe"]
        else:
            raise ValueError("Node ", node, " has no recipe")

    def get_args(self, node):
        attributes = self.nodes[node]
        if "args" in attributes and attributes["args"] is not None:
            return attributes["args"]
        else:
            raise ValueError("Node ", node, " has no args")

    def get_kwargs(self, node):
        attributes = self.nodes[node]
        if "kwargs" in attributes and attributes["kwargs"] is not None:
            return attributes["kwargs"]
        else:
            raise ValueError("Node ", node, " has no kwargs")

    def get_conditions(self, node):
        attributes = self.nodes[node]
        if "conditions" in attributes and attributes["conditions"] is not None:
            return attributes["conditions"]
        else:
            raise ValueError("Node ", node, " has no conditions")

    def get_possibilities(self, node):
        attributes = self.nodes[node]
        if "possibilities" in attributes and attributes["possibilities"] is not None:
            return attributes["possibilities"]
        else:
            raise ValueError("Node ", node, " has no possibilities")

    def clear_values(self):
        """
        Clear all values in the graph nodes.
        """
        for node in self.nodes:
            if self.nodes[node]["is_frozen"]:
                continue
            self.nodes[node]["has_value"] = False

    def update_internal_context(self, dictionary):
        """
        Update internal context with a dictionary.

        Parameters
        ----------
        dictionary: dict
            Dictionary with the new values
        """
        for key, value in dictionary.items():
            # Accept dictionaries with more keys than needed
            if key in self.nodes:
                self.nodes[key]["value"] = value
                self.nodes[key]["has_value"] = True

    def set_internal_context(self, dictionary):
        """
        Clear all values and then set a new internal context with a dictionary.

        Parameters
        ----------
        dictionary: dict
            Dictionary with the new values
        """
        self.clear_values()
        self.update_internal_context(dictionary)

    def get_internal_context(self, exclude_recipes=False):
        """
        Get the internal context.

        Parameters
        ----------
        exclude_recipes: bool
            Whether to exclude recipes from the returned dictionary or keep them.
        """
        if exclude_recipes:
            return {key: self.nodes[key]["value"] for key in self.nodes if (self.nodes[key]["has_value"] and not self.is_recipe(self.nodes[key]))}
        else:
            return {key: self.nodes[key]["value"] for key in self.nodes if self.nodes[key]["has_value"]}

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
            res.append(self.nodes[key]["value"])
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
        return {key: self.nodes[key]["value"] for key in list_of_keys}

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
        return {key: self.nodes[value]["value"] for key, value in dictionary.items()}

    def evaluate_target(self, target):
        """
        Generic interface to evaluate a GenericNode.
        """
        attributes = self.nodes[target]
        if "type" in attributes and attributes["type"] == "standard":
            return self.evaluate_standard(target)
        elif "type" in attributes and attributes["type"] == "conditional":
            return self.evaluate_conditional(target)
        elif "type" in attributes:
            raise ValueError("Evaluation of nodes of type ", attributes["type"], " is not supported")
        else:
            raise ValueError("Node ", target, " has no type")

    def evaluate_standard(self, node):
        """
        Evaluate of a node.
        """
        # Check if it already has a value
        if self.nodes[node]["has_value"]:
            return self.nodes[node]["value"]
        # If not, evaluate all arguments
        for dependency_name in self._nxdg.predecessors(node):
            self.evaluate_target(dependency_name)

        # Actual computation happens here
        try:
            recipe = self.get_recipe(node)
            func = self.nodes[recipe]["value"]
            res = func(*self.get_list_of_values(self.get_args(node)), **self.get_kwargs_values(self.get_kwargs(node)))
        except Exception as e:
            if len(e.args) > 0:
                e.args = ("While evaluating " + node + ": " + e.args[0],) + e.args[1:]
            raise
        # Save results
        self.nodes[node]["value"] = res
        self.nodes[node]["has_value"] = True
        return res

    def evaluate_conditional(self, conditional):
        """
        Evaluate a conditional.
        """
        # Check if it already has a value
        if self.nodes[conditional]["has_value"]:
            return self.nodes[conditional]["value"]
        # If not, evaluate the conditions until one is found true
        for index, condition in enumerate(self.get_conditions(conditional)):
            res = self.evaluate_target(condition)
            if res:
                break
        else:  # Happens if loop is never broken, i.e. when no conditions are true
            index = -1

        # Actual computation happens here
        res = self.evaluate_target(self.get_possibilities(conditional)[index])
        # Save results and release
        self.nodes[conditional]["value"] = res
        self.nodes[conditional]["has_value"] = True
        return res

    def execute_to_targets(self, *targets):
        """
        Evaluate all nodes in the graph that are needed to reach the targets.
        """
        for target in targets:
            self.evaluate_target(target)

    def is_other_node_compatible(self, node, other, other_node):
        this_attributes = self.nodes[node]
        other_attributes = other._nxdg.nodes[other_node]
        # If types differ, return False
        if this_attributes["type"] != other_attributes["type"]:
            return False
        # If nodes are equal, return True
        if this_attributes == other_attributes:
            return True
        # If they both have values but they differ, return False. If only one has a value, proceed
        if this_attributes["has_value"] and other_attributes["has_value"] and this_attributes["value"] != other_attributes["value"]:
            return False
        # If they both have dependencies but they differ, return False. If only one has dependencies, proceed
        if len(list(self._nxdg.predecessors(node))) != 0 and len(list(other._nxdg.predecessors(other_node))) != 0 and self._nxdg.predecessors(node) != other._nxdg.predecessors(other_node):
            return False
        # Return True if at least one has no dependencies (or they are the same), at least one has no value (or they are the same)
        return True

    def is_compatible(self, other):
        """
        Check if self and other can be composed. Currently DAG status is not verified.
        """
        if not isinstance(other, Graph):
            return False
        common_nodes = self.nodes & other._nxdg.nodes  # Intersection
        for key in common_nodes:
            if not self.is_other_node_compatible(key, other, key):
                return False
        return True

    def merge(self, other):
        """
        Merge other into self.
        """
        if not self.is_compatible(other):
            raise ValueError("Cannot merge incompatible graphs")
        res = nx.compose(self._nxdg, other._nxdg)
        self._nxdg = res

    def simplify_dependency(self, node_name, dependency_name):
        # Make everything a keyword argument. This is the fate of a simplified node
        self.get_kwargs(node_name).update({argument: argument for argument in self.get_args(node_name)})
        # Build lists of dependencies
        func_dependencies = list(self.get_kwargs(node_name).values())
        subfuncs = []
        subfuncs_dependencies = []
        for argument in self.get_kwargs(node_name):
            if argument == dependency_name:
                subfuncs.append(self[self.get_recipe(dependency_name)])  # Get python function
                subfuncs_dependencies.append(list(self.get_args(dependency_name)) + list(self.get_kwargs(dependency_name).values()))
            else:
                subfuncs.append(function_composer.identity_token)
                subfuncs_dependencies.append([argument])
        # Compose the functions
        self[self.get_recipe(node_name)] = function_composer.function_compose_simple(self[self.get_recipe(node_name)], subfuncs, func_dependencies, subfuncs_dependencies)
        # Change edges
        self._nxdg.remove_edge(dependency_name, node_name)
        for argument in self.get_args(dependency_name) + tuple(self.get_kwargs(dependency_name).values()):
            self._nxdg.add_edge(argument, node_name, accessor=argument)
        # Update node
        self.nodes[node_name]["args"] = ()
        self.get_kwargs(node_name).update({argument: argument for argument in self.get_args(dependency_name) + tuple(self.get_kwargs(dependency_name).values())})
        self.nodes[node_name]["kwargs"] = {key: value for key, value in self.get_kwargs(node_name).items() if value != dependency_name}

    def simplify_all_dependencies(self, node_name, exclude=[]):
        dependencies = self.get_args(node_name) + tuple(self.get_kwargs(node_name).values())
        for dependency in dependencies:
            if dependency not in exclude and self.nodes[dependency]["type"] == "standard":
                self.simplify_dependency(node_name, dependency)

    def freeze(self, *args):
        if len(args) == 0:  # Interpret as "Freeze everything"
            nodes_to_freeze = self.nodes
        else:
            nodes_to_freeze = args

        for key in nodes_to_freeze:
            if self.nodes[key]["has_value"]:
                self.nodes[key]["is_frozen"] = True

    def unfreeze(self, *args):
        if len(args) == 0:  # Interpret as "Unfreeze everything"
            nodes_to_unfreeze = self.nodes.keys()
        else:
            nodes_to_unfreeze = args

        for key in nodes_to_unfreeze:
            self.nodes[key]["is_frozen"] = False

    def make_recipe_dependencies_also_recipes(self):
        """
        Make dependencies (parents) of recipes also recipes
        """
        for node in self.nodes:
            if self.is_recipe(node):
                for parent in self._nxdg.predecessors(node):
                    self.nodes[parent]["is_recipe"] = True

    def finalize_definition(self):
        """
        Perform operations that should typically be done after the definition of a graph is completed

        Currently, this freezes all values, because it is assumed that values given during definition are to be frozen.
        It also marks dependencies of recipes as recipes themselves.
        """
        self.make_recipe_dependencies_also_recipes()
        self.freeze()
