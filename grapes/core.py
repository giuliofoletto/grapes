"""
Core of the grapes package. Includes the classes for nodes and graphs.

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
        return self.get_value(node)

    def __setitem__(self, node, value):
        """
        Set the value of a node with []
        """
        self.set_value(node, value)

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
            # Avoid adding existing node so as not to overwrite attributes
            if name not in self.nodes:
                self._nxdg.add_node(name, **starting_node_properties)

        else:  # Standard case
            # Add the node
            # Avoid adding existing node so as not to overwrite attributes
            if name not in self.nodes:
                self._nxdg.add_node(name, **starting_node_properties)
            # Set attributes
            # Note: This could be done in the constructor, but doing it separately adds flexibility
            # Indeed, we might want to change how attributes work, and we can do it by modifying setters
            self.set_recipe(name, recipe)
            self.set_args(name, args)
            self.set_kwargs(name, kwargs)

            # Add and connect the recipe
            # Avoid adding existing recipe so as not to overwrite attributes
            if recipe not in self.nodes:
                self._nxdg.add_node(recipe, **starting_node_properties)
            self.set_is_recipe(recipe, True)
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
        self.set_type(name, "conditional")

        # Add conditions name to the list of conditions of the conditional
        self.set_conditions(name, [condition])

        # Add possibilities to the list of possibilities of the conditional
        self.set_possibilities(name, [value_true, value_false])

    def get_node_attribute(self, node, attribute):
        attributes = self.nodes[node]
        if attribute in attributes and attributes[attribute] is not None:
            return attributes[attribute]
        else:
            raise ValueError("Node ", node, " has no ", attribute)

    def set_node_attribute(self, node, attribute, value):
        self.nodes[node][attribute] = value

    def is_recipe(self, node):
        return self.get_node_attribute(node, "is_recipe")

    def set_is_recipe(self, node, is_recipe):
        return self.set_node_attribute(node, "is_recipe", is_recipe)

    def get_recipe(self, node):
        return self.get_node_attribute(node, "recipe")

    def set_recipe(self, node, recipe):
        return self.set_node_attribute(node, "recipe", recipe)

    def get_args(self, node):
        return self.get_node_attribute(node, "args")

    def set_args(self, node, args):
        return self.set_node_attribute(node, "args", args)

    def get_kwargs(self, node):
        return self.get_node_attribute(node, "kwargs")

    def set_kwargs(self, node, kwargs):
        return self.set_node_attribute(node, "kwargs", kwargs)

    def get_conditions(self, node):
        return self.get_node_attribute(node, "conditions")

    def set_conditions(self, node, conditions):
        return self.set_node_attribute(node, "conditions", conditions)

    def get_possibilities(self, node):
        return self.get_node_attribute(node, "possibilities")

    def set_possibilities(self, node, possibilities):
        return self.set_node_attribute(node, "possibilities", possibilities)

    def get_type(self, node):
        return self.get_node_attribute(node, "type")

    def set_type(self, node, type):
        return self.set_node_attribute(node, "type", type)

    def get_value(self, node):
        attributes = self.nodes[node]
        if "value" in attributes and attributes["value"] is not None and self.nodes[node]["has_value"]:
            return attributes["value"]
        else:
            raise ValueError("Node ", node, " has no value")

    def set_value(self, node, value):
        self.nodes[node]["value"] = value
        self.nodes[node]["has_value"] = True

    def unset_value(self, node):
        self.nodes[node]["has_value"] = False

    def is_frozen(self, node):
        return self.get_node_attribute(node, "is_frozen")

    def set_is_frozen(self, node, is_frozen):
        return self.set_node_attribute(node, "is_frozen", is_frozen)

    def has_value(self, node):
        return self.get_node_attribute(node, "has_value")

    def set_has_value(self, node, has_value):
        return self.set_node_attribute(node, "has_value", has_value)

    def clear_values(self):
        """
        Clear all values in the graph nodes.
        """
        for node in self.nodes:
            if self.is_frozen(node):
                continue
            self.unset_value(node)

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
                self.set_value(key, value)

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
            return {key: self.get_value(key) for key in self.nodes if (self.has_value(key) and not self.is_recipe(key))}
        else:
            return {key: self.get_value(key) for key in self.nodes if self.has_value(key)}

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
            res.append(self.get_value(key))
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
        return {key: self.get_value(key) for key in list_of_keys}

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
        return {key: self.get_value(value) for key, value in dictionary.items()}

    def evaluate_target(self, target):
        """
        Generic interface to evaluate a GenericNode.
        """
        if self.get_type(target) == "standard":
            return self.evaluate_standard(target)
        elif self.get_type(target) == "conditional":
            return self.evaluate_conditional(target)
        else:
            raise ValueError("Evaluation of nodes of type ", self.get_type(target), " is not supported")

    def evaluate_standard(self, node):
        """
        Evaluate of a node.
        """
        # Check if it already has a value
        if self.has_value(node):
            return self.get_value(node)
        # If not, evaluate all arguments
        for dependency_name in self._nxdg.predecessors(node):
            self.evaluate_target(dependency_name)

        # Actual computation happens here
        try:
            recipe = self.get_recipe(node)
            func = self.get_value(recipe)
            res = func(*self.get_list_of_values(self.get_args(node)), **self.get_kwargs_values(self.get_kwargs(node)))
        except Exception as e:
            if len(e.args) > 0:
                e.args = ("While evaluating " + node + ": " + e.args[0],) + e.args[1:]
            raise
        # Save results
        self.set_value(node, res)
        return res

    def evaluate_conditional(self, conditional):
        """
        Evaluate a conditional.
        """
        # Check if it already has a value
        if self.has_value(conditional):
            return self.get_value(conditional)
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
        self.set_value(conditional, res)
        return res

    def execute_to_targets(self, *targets):
        """
        Evaluate all nodes in the graph that are needed to reach the targets.
        """
        for target in targets:
            self.evaluate_target(target)

    def is_other_node_compatible(self, node, other, other_node):
        # If types differ, return False
        if self.get_type(node) != other.get_type(other_node):
            return False
        # If nodes are equal, return True
        if self.nodes[node] == other._nxdg.nodes[other_node]:
            return True
        # If they both have values but they differ, return False. If only one has a value, proceed
        if self.has_value(node) and other.has_value(other_node) and self.get_value(node) != other.get_value(other_node):
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
        # Refresh alias for easy access
        self.nodes = self._nxdg.nodes

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
        self.set_args(node_name, ())
        new_kwargs = self.get_kwargs(node_name)
        new_kwargs.update({argument: argument for argument in self.get_args(dependency_name) + tuple(self.get_kwargs(dependency_name).values())})
        new_kwargs = {key: value for key, value in new_kwargs.items() if value != dependency_name}
        self.set_kwargs(node_name, new_kwargs)

    def simplify_all_dependencies(self, node_name, exclude=[]):
        dependencies = self.get_args(node_name) + tuple(self.get_kwargs(node_name).values())
        for dependency in dependencies:
            if dependency not in exclude and self.get_type(dependency) == "standard":
                self.simplify_dependency(node_name, dependency)

    def freeze(self, *args):
        if len(args) == 0:  # Interpret as "Freeze everything"
            nodes_to_freeze = self.nodes
        else:
            nodes_to_freeze = args

        for key in nodes_to_freeze:
            if self.has_value(key):
                self.set_is_frozen(key, True)

    def unfreeze(self, *args):
        if len(args) == 0:  # Interpret as "Unfreeze everything"
            nodes_to_unfreeze = self.nodes.keys()
        else:
            nodes_to_unfreeze = args

        for key in nodes_to_unfreeze:
            self.set_is_frozen(key, False)

    def make_recipe_dependencies_also_recipes(self):
        """
        Make dependencies (parents) of recipes also recipes
        """
        for node in self.nodes:
            if self.is_recipe(node):
                for parent in self._nxdg.predecessors(node):
                    self.set_is_recipe(parent, True)

    def finalize_definition(self):
        """
        Perform operations that should typically be done after the definition of a graph is completed

        Currently, this freezes all values, because it is assumed that values given during definition are to be frozen.
        It also marks dependencies of recipes as recipes themselves.
        """
        self.make_recipe_dependencies_also_recipes()
        self.freeze()
