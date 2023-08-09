import owlready2 as owl
import itertools as it

from owlready2 import Thing

from lcall.DLPropertyChain import DLPropertyChain
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion
from lcall.owlRdyClass import OwlRdyClass
from lcall.abstractReasoner import AbstractReasoner
from lcall.callFormula import CallFormula
from lcall.httpFunction import HTTPFunction
from lcall.owlRdyDatatype import OwlRdyDatatype
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyInstance import OwlRdyInstance
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.pythonFunction import PythonFunction


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
            item_called_function = call.functionToCall[item][0]
            if item_called_function in call.PythonFunction.instances():
                call_expr = item_called_function.hasPyExpr
                call_exec = item_called_function.hasPyExec
                called_function = PythonFunction(call_expr, call_exec)
            elif item_called_function in call.HTTPFunction.instances():
                call_url = item_called_function.hasHttpURL
                call_auth = item_called_function.hasHttpAuth
                called_function = HTTPFunction(call_url, call_auth)
            item_params_list = self._build_param_list(call.hasParams[item][0])
            item_domain = call.domain[item][0]
            item_range = call.range[item][0]
            formula = CallFormula(OwlRdyDatatypeProperty(item_subsumes), called_function, item_params_list,
                                  OwlRdyClass(item_domain), OwlRdyDatatype(item_range))
            self.calls.append(formula)

    def _build_param_list(self, params: Thing) -> list[DLPropertyChain]:
        """
        Build the list of parameters (property chains) from a call:ParamList instance

        :param params: call:ParamList instance of the parameters
        :return: list of parameters (property chains)
        """
        call = owl.get_namespace("https://k.loria.fr/ontologies/call")
        param_list = []
        while params is not None:
            # Get property chain from parameter
            prop_chain = call.paramListHead[params][0]
            # Get datatype property of the chain
            datatype_prop = OwlRdyDatatypeProperty(call.hasDatatypeProperty[prop_chain][0])

            # Build object property chain
            object_prop = []
            object_prop_chain_onto = call.hasObjectPropertyList[prop_chain]
            object_prop_chain = object_prop_chain_onto[0] if len(object_prop_chain_onto) != 0 else None

            while object_prop_chain is not None:
                object_prop.append(OwlRdyObjectProperty(call.objectPropertyListHead[object_prop_chain][0]))
                object_prop_chain_onto = call.hasObjectPropertyList[object_prop_chain]
                object_prop_chain = object_prop_chain_onto[0] if len(object_prop_chain_onto) != 0 else None

            # Add property chain to the python parameter list
            param_list.append(DLPropertyChain(datatype_prop, *object_prop))

            # Get next item in param list
            params_onto = call.paramListTail[params]
            params = params_onto[0] if len(params_onto) != 0 else None

        return param_list

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

    def is_asserted(self, assertion: DatatypePropertyAssertion) -> bool:
        """
        Checks if the given assertion is already true in the ontology

        :param assertion: assertion to test
        :return: true if the assertion is already in the ontology, false otherwise
        """
        instance = assertion.get_instance().get()
        base_prop = assertion.get_datatype_property().get()
        prop = base_prop[instance]
        value = assertion.get_value()

        # Get first datatype in property range (as we can't know which one it will be)
        prop_type = base_prop.range[0]
        if prop_type is not None:
            # Cast value result as wanted type
            if prop_type is bool:
                value = value not in ("false", "False", "0", False, 0)
            value = prop_type(value)

        if isinstance(prop, list):
            for item in prop:
                if item == value:
                    return True
        elif prop is not None and prop == value:
            return True
        else:
            return False

    def add_assertions(self, assertions: list[DatatypePropertyAssertion]):
        """
        Add assertions to the ontology

        :param assertions: assertions to add
        """
        for assertion in assertions:
            instance = assertion.get_instance().get()
            base_prop = assertion.get_datatype_property().get()
            prop = base_prop[instance]
            value = assertion.get_value()

            # Get first datatype in property range (as we can't know which one it will be)
            prop_type = base_prop.range[0]
            if prop_type is not None:
                # Cast value result as wanted type
                if prop_type is bool:
                    value = value not in ("false", "False", "0", False, 0)
                value = prop_type(value)

            # Add the value asserted in the list
            prop.append(value)

        # Resync reasoner as we modified
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)
