import owlready2 as owl
import itertools as it

from lcall.DLPropertyChain import DLPropertyChain
from lcall.propertyAssertion import PropertyAssertion
from lcall.owlRdyClass import OwlRdyClass
from lcall.abstractReasoner import AbstractReasoner
from lcall.callFormula import CallFormula
from lcall.multipleFunctionCall import MultipleFunctionCall
from lcall.datatypeFunctionCall import DatatypeFunctionCall
from lcall.owlRdyDatatype import OwlRdyDatatype
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyInstance import OwlRdyInstance
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty


class OwlRdyReasoner(AbstractReasoner):
    """
    Implementation of the reasoner interface with owlready2

    The ontology is stored in the 'onto' instance attribute.
    """

    def __init__(self, onto_iri: str, local_path: str):
        """
        Loads ontology and performs initial reasoner sync

        :param onto_iri: iri of the ontology
        :param local_path: local path to search ontology files if offline
        """
        owl.onto_path.append(local_path)
        self.onto = owl.get_ontology(onto_iri).load()
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)

        self.calls = []

        call = owl.get_namespace("https://k.loria.fr/ontologies/call")
        for item in call.CallFormula.instances():
            # Get all call:CallFormula instances and creates python CallFormula instances from them
            item_subsumes = call.subsumingProperty[item][0]
            item_function_calls = call.hasFunctionCall[item][0]
            if isinstance(item_function_calls, call.FunctionCallList):
                item_function_calls = MultipleFunctionCall(item_function_calls, call)
            else:
                item_function_calls = DatatypeFunctionCall(item_function_calls, call)
            item_domain = call.domain[item][0]
            item_range = call.range[item][0]
            # if the range is a domain and not a datatype
            if isinstance(item_range, owl.ThingClass):
                item_subsumes = OwlRdyObjectProperty(item_subsumes)
                item_range = OwlRdyClass(item_range)
            else:
                item_subsumes = OwlRdyDatatypeProperty(item_subsumes)
                item_range = OwlRdyDatatype(item_range)

            # if there is a problem with the nested functionCalls, it returns None
            if item_function_calls:
                formula = CallFormula(item.name, item_subsumes, item_function_calls,
                                  OwlRdyClass(item_domain), item_range)
                self.calls.append(formula)


    def instances(self) -> list[OwlRdyInstance]:
        """
        Get individuals of the ontology

        :return: individuals of the ontology
        """
        res = []
        for ind in self.onto.individuals():
            res.append(OwlRdyInstance(ind))
        return res

    def _is_instance_of(self, instance: OwlRdyInstance, class_expression: OwlRdyClass) -> bool:
        """
        Checks if the given instance is in a given concept

        :param instance: instance to check
        :param class_expression: class expression to check
        :return: true if the instance is in the class, false otherwise
        """
        onto_instance = instance.get()
        for item in self.onto.search(is_a=class_expression.get()):
            if onto_instance.name == item.name:
                return True
        return False

    def list_val_params(self, instance: OwlRdyInstance, params: list[DLPropertyChain]) -> list:
        """
        Gets parameter combinations for an instance

        :param instance: instance to get values from
        :param params: list of parameters (property chains)
        :return: parameter combinations for the instance
        """
        list_values = []
        base_instance = instance.get()
        for param in params:
            # Start with the given instance
            current_list = [base_instance]
            # Follow the property chain
            for dl_prop in param:
                prop = dl_prop.get()
                next_list = []
                # Build a list of results for the current property
                for instance in current_list:
                    next_list.extend(prop[instance])
                # Make the list the current one for iteration
                current_list = next_list
            # Add the final values to the list (end of property chain)
            list_values.append(current_list)
        res_list = it.product(*list_values)
        return res_list

    def calls_for_instance(self, instance: OwlRdyInstance) -> list[CallFormula]:
        """
        Gets call formulas where the instance is in its domain

        :param instance: instance to check
        :return: call objects of the ontology for the given instance
        """
        call_list = []
        for call in self.calls:
            domain = call.get_domain()
            if domain is None or self._is_instance_of(instance, domain):
                call_list.append(call)
        return call_list

    def is_asserted(self, assertion: PropertyAssertion) -> bool:
        """
        Checks if the given assertion is already true in the ontology

        :param assertion: assertion to test
        :return: true if the assertion is already in the ontology, false otherwise
        """
        instance = assertion.get_instance().get()
        
        base_prop = assertion.get_property().get()
        prop = base_prop[instance]
        value = assertion.get_value()

        if isinstance(prop, list):
            for item in prop:
                if item == value:
                    return True
        elif prop is not None and prop == value:
            return True
        else:
            return False

    def add_assertions(self, assertions: list[PropertyAssertion]):
        """
        Add assertions to the ontology

        :param assertions: assertions to add
        """
        for assertion in assertions:
            instance = assertion.get_instance().get()
            base_prop = assertion.get_property().get()
            prop = base_prop[instance]
            value = assertion.get_value()

            # Add the value asserted in the list
            prop.append(value)
        # Resync reasoner as we modified
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)
