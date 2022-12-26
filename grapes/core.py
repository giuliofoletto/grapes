"""
Core of the grapes package. Includes the classes for nodes and graphs.

Author: Giulio Foletto <giulio.foletto@outlook.com>.
License: See project-level license file.
"""

from typing import ValuesView
import networkx as nx
from . import function_composer
import inspect


starting_node_properties = {"type": "standard", "has_value": False, "value": None, "is_frozen": False, "is_recipe": False, "topological_generation_index": -1}


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
            # The node is readded even if already existing
            self._nxdg.add_node(name, **starting_node_properties)

        else:  # Standard case
            # Add the node
            # The node is readded even if already existing
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

    def add_step_quick(self, name, recipe):
        """
        Interface to quickly add a step by passing a name and a function.

        The recipe node takes the name of the passed function.
        Dependency nodes are built from the args and kwonlyargs of the passed function.
        """
        # Check that the passed recipe is a valid function
        if not inspect.isfunction(recipe):
            raise TypeError("The passed recipe should be a function, but it is a " + type(recipe))
        argspec = inspect.getfullargspec(recipe)
        # varargs and varkw are not supported because add_step_quick needs parameter names to build nodes
        if argspec.varargs is not None or argspec.varkw is not None:
            raise ValueError("Functions with varargs or varkwargs are not supported by add_step_quick because there would be no way to name dependency nodes")

        # Get function name and parameters
        recipe_name = recipe.__name__
        # Lambdas are all automatically named "<lambda>" so we change this
        if recipe_name == "<lambda>":
            recipe_name = "recipe_for_" + name
        args = argspec.args
        kwargs_list = argspec.kwonlyargs
        # Build a dictionary with identical keys and values so that recipe is called all the keys are used are kwargs
        kwargs = {kw: kw for kw in kwargs_list}
        # Add the step: this will create nodes for name, recipe_name and all elements of args and kwargs_list
        self.add_step(name, recipe_name, *args, **kwargs)
        # Directly set the value of recipe_name to recipe
        self.set_value(recipe_name, recipe)

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

    def add_multiple_conditional(self, name, conditions, possibilities):
        """
        Interface to add a multiple conditional to the graph.
        """
        # Add all nodes and connect all edges
        self._nxdg.add_node(name, **starting_node_properties)
        for node in conditions + possibilities:
            # Avoid adding existing dependencies so as not to overwrite attributes
            if node not in self.nodes:
                self._nxdg.add_node(node, **starting_node_properties)
            self._nxdg.add_edge(node, name)

        # Specify that this node is a conditional
        self.set_type(name, "conditional")

        # Add conditions name to the list of conditions of the conditional
        self.set_conditions(name, conditions)

        # Add possibilities to the list of possibilities of the conditional
        self.set_possibilities(name, possibilities)

    def edit_step(self, name, recipe=None, *args, **kwargs):
        """
        Interface to edit an existing node, changing its predecessors
        """
        if name not in self.nodes:
            raise ValueError("Cannot edit non-existent node " + name)

        # Store old attributes
        was_recipe = self.is_recipe(name)
        was_frozen = self.is_frozen(name)
        had_value = self.has_value(name)
        if had_value:
            old_value = self.get_value(name)

        # Remove in-edges from the node because we need to replace them
        # use of list() is to make a copy because in_edges() returns a view
        self._nxdg.remove_edges_from(list(self._nxdg.in_edges(name)))
        # Readd the step. This should not break anything
        self.add_step(name, recipe, *args, **kwargs)

        # Readd attributes
        # Readding out-edges is not needed because we never removed them
        self.set_is_recipe(name, was_recipe)
        self.set_is_frozen(name, was_frozen)
        self.set_has_value(name, had_value)
        if had_value:
            self.set_value(name, old_value)

    def remove_step(self, name):
        """
        Interface to remove an existing node, without changing anything else
        """
        if name not in self.nodes:
            raise ValueError("Cannot edit non-existent node " + name)
        self._nxdg.remove_node(name)

    def get_node_attribute(self, node, attribute):
        attributes = self.nodes[node]
        if attribute in attributes and attributes[attribute] is not None:
            return attributes[attribute]
        else:
            raise ValueError("Node " + node + " has no " + attribute)

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
        conditions = self.get_node_attribute(node, "conditions")
        if not isinstance(conditions, list):
            conditions = list(conditions)
        return conditions

    def set_conditions(self, node, conditions):
        if not isinstance(conditions, list):
            conditions = list(conditions)
        return self.set_node_attribute(node, "conditions", conditions)

    def get_possibilities(self, node):
        possibilities = self.get_node_attribute(node, "possibilities")
        if not isinstance(possibilities, list):
            possibilities = list(possibilities)
        return possibilities

    def set_possibilities(self, node, possibilities):
        if not isinstance(possibilities, list):
            possibilities = list(possibilities)
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
            raise ValueError("Node " + node + " has no value")

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

    def clear_values(self, *args):
        """
        Clear values in the graph nodes.
        """
        if len(args) == 0:  # Interpret as "Clear everything"
            nodes_to_clear = self.nodes
        else:
            nodes_to_clear = args & self.nodes  # Intersection

        for node in nodes_to_clear:
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

    def evaluate_target(self, target, continue_on_fail=False):
        """
        Generic interface to evaluate a GenericNode.
        """
        if self.get_type(target) == "standard":
            return self.evaluate_standard(target, continue_on_fail)
        elif self.get_type(target) == "conditional":
            return self.evaluate_conditional(target, continue_on_fail)
        else:
            raise ValueError("Evaluation of nodes of type " + self.get_type(target) + " is not supported")

    def evaluate_standard(self, node, continue_on_fail=False):
        """
        Evaluate of a node.
        """
        # Check if it already has a value
        if self.has_value(node):
            self.get_value(node)
            return
        # If not, evaluate all arguments
        for dependency_name in self._nxdg.predecessors(node):
            self.evaluate_target(dependency_name, continue_on_fail)

        # Actual computation happens here
        try:
            recipe = self.get_recipe(node)
            func = self.get_value(recipe)
            res = func(*self.get_list_of_values(self.get_args(node)), **self.get_kwargs_values(self.get_kwargs(node)))
        except Exception as e:
            if continue_on_fail:
                # Do nothing, we want to keep going
                return
            else:
                if len(e.args) > 0:
                    e.args = ("While evaluating " + node + ": " + str(e.args[0]),) + e.args[1:]
                raise
        # Save results
        self.set_value(node, res)

    def evaluate_conditional(self, conditional, continue_on_fail=False):
        """
        Evaluate a conditional.
        """
        # Check if it already has a value
        if self.has_value(conditional):
            self.get_value(conditional)
            return
        # If not, evaluate the conditions until one is found true
        for index, condition in enumerate(self.get_conditions(conditional)):
            self.evaluate_target(condition, continue_on_fail)
            if self.has_value(condition) and self.get_value(condition):
                break
            elif not self.has_value(condition):
                # Computing failed
                if continue_on_fail:
                    # Do nothing, we want to keep going
                    return
                else:
                    raise ValueError("Node " + condition + " could not be computed")
        else:  # Happens if loop is never broken, i.e. when no conditions are true
            index = -1

        # Actual computation happens here
        try:
            possibility = self.get_possibilities(conditional)[index]
            self.evaluate_target(possibility, continue_on_fail)
            res = self.get_value(possibility)
        except:
            if continue_on_fail:
                # Do nothing, we want to keep going
                return
            else:
                raise ValueError("Node " + possibility + " could not be computed")
        # Save results and release
        self.set_value(conditional, res)

    def execute_to_targets(self, *targets):
        """
        Evaluate all nodes in the graph that are needed to reach the targets.
        """
        for target in targets:
            self.evaluate_target(target, False)

    def progress_towards_targets(self, *targets):
        """
        Move towards the targets by evaluating nodes, but keep going if evaluation fails.
        """
        for target in targets:
            self.evaluate_target(target, True)

    def find_reachability_target(self, target):
        """
        Generic interface to find the reachability of a GenericNode.
        """
        if self.get_type(target) == "standard":
            return self.find_reachability_standard(target)
        elif self.get_type(target) == "conditional":
            return self.find_reachability_conditional(target)
        else:
            raise ValueError("Finding the reachability of nodes of type " + self.get_type(target) + " is not supported")

    def find_reachability_standard(self, node):
        """
        Find the reachability of a standard node.
        """
        # Check if it already has a value
        if self.has_value(node):
            self.get_value(node)
            return "reachable", set()
        # If not, check the missing dependencies of all arguments
        dependencies = set(self._nxdg.predecessors(node))
        if len(dependencies) == 0:
            # If this node does not have predecessors (and does not have a value itself), it is a missing dependency
            missing_dependencies = set()
            missing_dependencies.add(node)
            return "unreachable", missing_dependencies
        else:
            # Otherwise, dependencies must be checked
            missing_dependencies = set()
            reachability = "reachable"
            for dependency_name in dependencies:
                reachability, missing_dependencies = self.get_updated_reachability(*self.find_reachability_target(dependency_name), reachability, missing_dependencies)
            return reachability, missing_dependencies

    def find_reachability_conditional(self, conditional):
        """
        Find the reachability of a conditional.
        """
        # Check if it already has a value
        if self.has_value(conditional):
            self.get_value(conditional)
            return "reachable", set()
        # If not, evaluate the conditions until one is found true
        for index, condition in enumerate(self.get_conditions(conditional)):
            if self.has_value(condition) and self.get_value(condition):
                # A condition is true
                possibility = self.get_possibilities(conditional)[index]
                return self.find_reachability_target(possibility)
        else:
            # Happens if loop is never broken, i.e. when no conditions are true
            # If all conditions and possibilities are reachable -> reachable
            # If all conditions and possibilities are unreachable -> unreachable
            # If some conditions are reachable or uncertain but the corresponding possibilities are all unreachable -> unreachable
            # In all other cases -> uncertain
            list_reachabilities_conditions = []
            list_missing_dependencies_conditions = []
            list_reachabilities_possibilities = []
            list_missing_dependencies_possibilities = []
            for condition in self.get_conditions(conditional):
                reachability, missing_dependencies = self.find_reachability_target(condition)
                list_reachabilities_conditions.append(reachability)
                list_missing_dependencies_conditions.append(missing_dependencies)
            for possibility in self.get_possibilities(conditional):
                reachability, missing_dependencies = self.find_reachability_target(possibility)
                list_reachabilities_possibilities.append(reachability)
                list_missing_dependencies_possibilities.append(missing_dependencies)
            if "uncertain" not in list_reachabilities_conditions+list_reachabilities_possibilities and "unreachable" not in list_reachabilities_conditions+list_reachabilities_possibilities:
                # All conditions and possibilities are reachable -> reachable
                return "reachable", set()
            elif "uncertain" not in list_reachabilities_conditions+list_reachabilities_possibilities and "reachable" not in list_reachabilities_conditions+list_reachabilities_possibilities:
                # All conditions and possibilities are unreachable -> unreachable
                return "unreachable", set().union(*(list_missing_dependencies_conditions+list_missing_dependencies_possibilities))
            else:
                not_unreachable_condition_indexes = [i for i, x in enumerate(list_reachabilities_conditions) if x != "unreachable"]
                sublist_reachabilities_possibilities = []
                for index in not_unreachable_condition_indexes:
                    sublist_reachabilities_possibilities.append(list_reachabilities_possibilities[index])
                if "uncertain" not in sublist_reachabilities_possibilities and "reachable" not in sublist_reachabilities_possibilities:
                    # All corresponding possibilities are unreachable -> unreachable
                    return "unreachable", set().union(*(list_missing_dependencies_conditions+list_missing_dependencies_possibilities))
                else:
                    return "uncertain", set().union(*(list_missing_dependencies_conditions+list_missing_dependencies_possibilities))

    def get_updated_reachability(self, new_reachability, new_missing_dependencies, reachability="reachable", missing_dependencies=set()):
        if reachability in ("reachable", "uncertain") and new_reachability == "unreachable":
            reachability = "unreachable"
        elif reachability == "reachable" and new_reachability == "uncertain":
            reachability = "uncertain"
        return reachability, missing_dependencies.union(new_missing_dependencies)

    def find_reachability_targets(self, *targets):
        missing_dependencies = set()
        reachability = "reachable"
        for target in targets:
            reachability, missing_dependencies = self.get_updated_reachability(*self.find_reachability_target(target), reachability, missing_dependencies)
        return reachability, missing_dependencies

    def is_other_node_compatible(self, node, other, other_node):
        # If types differ, return False
        if self.get_type(node) != other.get_type(other_node):
            return False
        # If nodes are equal, return True
        if self.nodes[node] == other._nxdg.nodes[other_node]:
            return True
        # If they both have values but they differ, return False. If only one has a value, proceed
        if self.has_value(node) and other.has_value(other_node) and self.get_value(node) != other.get_value(other_node):
            # Plot twist! Both are functions and have the same code: proceed
            if inspect.isfunction(self.get_value(node)) and inspect.isfunction(other.get_value(other_node)) and self.get_value(node).__code__.co_code == other.get_value(other_node).__code__.co_code:
                pass
            else:
                return False
        # If they both have dependencies but they differ, return False. If only one has dependencies, proceed
        predecessors = list(self._nxdg.predecessors(node))
        other_predecessors = list(other._nxdg.predecessors(other_node))
        if len(predecessors) != 0 and len(other_predecessors) != 0 and predecessors != other_predecessors:
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
                if self.get_type(dependency_name) != "standard":
                    raise TypeError("Simplification only supports standard nodes, while the type of " + dependency_name + " is " + self.get_type(dependency_name))
                if self.get_type(self.get_recipe(dependency_name)) != "standard":
                    raise TypeError("Simplification only supports standard nodes, while the type of " + self.get_recipe(dependency_name) + " is " + self.get_type(self.get_recipe(dependency_name)))
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
            if dependency not in exclude:
                self.simplify_dependency(node_name, dependency)

    def freeze(self, *args):
        if len(args) == 0:  # Interpret as "Freeze everything"
            nodes_to_freeze = self.nodes
        else:
            nodes_to_freeze = args & self.nodes  # Intersection

        for key in nodes_to_freeze:
            if self.has_value(key):
                self.set_is_frozen(key, True)

    def unfreeze(self, *args):
        if len(args) == 0:  # Interpret as "Unfreeze everything"
            nodes_to_unfreeze = self.nodes.keys()
        else:
            nodes_to_unfreeze = args & self.nodes  # Intersection

        for key in nodes_to_unfreeze:
            self.set_is_frozen(key, False)

    def make_recipe_dependencies_also_recipes(self):
        """
        Make dependencies (parents) of recipes also recipes
        """
        # Work in reverse topological order, to get children before parents
        for node in reversed(self.get_topological_order()):
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
        self.update_topological_generation_indexes()
        self.freeze()

    def get_topological_order(self):
        """
        Return list of nodes in topological order, i.e., from dependencies to targets
        """
        return list(nx.topological_sort(self._nxdg))

    def get_topological_generations(self):
        """
        Return list of topological generations of the graph
        """
        return list(nx.topological_generations(self._nxdg))

    def update_topological_generation_indexes(self):
        generations = self.get_topological_generations()
        for node in self.nodes:
            for index, generation in enumerate(generations):
                if node in generation:
                    self.set_node_attribute(node, "topological_generation_index", index)
                    break
