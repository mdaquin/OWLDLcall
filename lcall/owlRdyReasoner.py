import owlready2 as owl
import itertools as it
import logging

from typing import Generator, ValuesView
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyClass import OwlRdyClass
from lcall.abstractReasoner import AbstractReasoner
from lcall.callFormula import CallFormula
from lcall.owlRdyDatatype import OwlRdyDatatype
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyInstance import OwlRdyInstance
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.pythonFunction import PythonFunction
from lcall.httpFunction import HTTPFunction
from lcall.classAssertion import ClassAssertion
from lcall.assertion import Assertion
from lcall.objectPropertyAssertion import ObjectPropertyAssertion
from lcall.datatypePropertyAssertion import DatatypePropertyAssertion


def get_function(function: owl.Thing, call: owl.Namespace) -> (PythonFunction | HTTPFunction):
    """
    Encapsulates the function

    :param function: the call:CallableThing instance (basically the function)
    :param call: the ontology namespace to get the call:CallableThing subclasses
    :return: the encapsulated function
    """
    if isinstance(function, call.PythonFunction):
        call_expr = function.hasPyExpr
        call_exec = function.hasPyExec
        called_function = PythonFunction(call_expr, call_exec)
    elif isinstance(function, call.HTTPFunction):
        call_url = function.hasHttpURL
        call_auth = function.hasHttpAuth
        called_function = HTTPFunction(call_url, call_auth)
    else:
        raise ValueError(f"{function} is not recognized as a function.")
    return called_function


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
        if not self.reason():
            logging.error("The given ontology is inconsistent.")
            exit(-1)

        self.calls = []

        # namespace for the call ontology
        call = owl.get_namespace("https://k.loria.fr/ontologies/call")
        # namespace for the given ontology
        self.namespace = owl.get_namespace(onto_iri)

        # remove the instances that aren't really instances
        self.instances = [OwlRdyInstance(ind) for ind in self.onto.individuals()
                          if not isinstance(ind, (call.CallableThing, call.ParamList,
                                                  call.PropertyChain, call.CallFormula))]

        # Get all call:CallFormula instances and creates python CallFormula instances from them
        for item in call.CallFormula.instances():
            try:
                self.calls.append(self.create_call(item, call))
            # if there is a problem with the call
            except ValueError as e:
                logging.warning(e)
                logging.info(f"call '{item}' ignored.")
                continue

    def create_call(self, call: owl.Thing, namespace: owl.Namespace) -> CallFormula:
        """
        Create a python CallFormula from a call from the ontology

        :param call: the call from the ontology
        :param namespace: the namespace of the call ontology
        :return: a python CallFormula
        """
        subsuming_prop = call.subsumingProperty
        function = call.functionToCall
        parameters = call.hasParams
        domain = call.domain
        _range = call.range

        # checks that the subsuming property is defined (required)
        if not subsuming_prop:
            raise ValueError(f"Subsuming property not defined for call '{call}'.")
        else:
            subsuming_prop = subsuming_prop[0]

        # check if the domain is defined
        if not domain:
            raise ValueError(f"Domain not defined for call '{call}'.")
        else:
            domain = domain[0]

        # check if the range is defined
        if not _range:
            raise ValueError(f"Range not defined for call '{call}'.")
        else:
            _range = _range[0]

        # encapsulate in classes and check cohesion between the types
        # for example, if the subsuming property is an object property, the range can't be a datatype

        # encapsulate the parameters list (propertyChain)
        parameters = self.build_param_list(parameters)

        # the subsuming property is an object property
        if isinstance(subsuming_prop, owl.ObjectPropertyClass):

            # verify that the range is a class
            if not isinstance(_range, owl.ThingClass):
                raise ValueError(f"Range '{_range}' is not compatible with the (object) subsuming property '"
                                 f"{subsuming_prop}' for call '{call}'.\nRange should be a class.")

            function = get_function(function, namespace)
            _range = OwlRdyClass(_range)
            subsuming_prop = OwlRdyObjectProperty(subsuming_prop)

        # the subsuming property is a datatype property
        elif isinstance(subsuming_prop, owl.DataPropertyClass):

            # verify that the range is a datatype
            # the range can be None if the datatype isn't supported by the library
            if _range is not None and not isinstance(_range, type):
                raise ValueError(f"Range '{_range}' is not compatible with the (datatype) subsuming property '"
                                 f"{subsuming_prop}' for call '{call}'.\nRange should be a datatype.")

            function = get_function(function, namespace)
            _range = OwlRdyDatatype(_range)
            subsuming_prop = OwlRdyDatatypeProperty(subsuming_prop)
        else:
            # if the subsuming property is not a property
            raise ValueError(f"Subsuming property '{subsuming_prop}' is not a property ({call}).")

        return CallFormula(call.name, subsuming_prop, function, parameters, OwlRdyClass(domain), _range)

    def build_param_list(self, params: owl.Thing) -> list[DLPropertyChain]:
        """
        Build the list of parameters (property chains) from a call:ParamList instance

        :param params: call:ParamList instance of the parameters
        :return: list of parameters (property chains)
        """
        param_list = []
        while params:
            # Get property chain from parameter
            prop_chain = params.head

            # if we don't find a propchain
            if not prop_chain:
                raise ValueError(str(params) + " missing a propChain head.")

            prop_chain = prop_chain[0]
            # if there is no head on this propchain
            if not prop_chain.head:
                raise ValueError(str(prop_chain) + " property chain doesn't have a head.")

            properties = []

            # Build object property chain
            _property = prop_chain.head[0]
            while isinstance(_property, owl.ObjectPropertyClass):
                properties.append(OwlRdyObjectProperty(_property))

                if prop_chain.tail and prop_chain.tail[0].head:
                    prop_chain = prop_chain.tail[0]
                    _property = prop_chain.head[0]
                else:
                    raise ValueError(str(prop_chain) + " tail missing OR tail head missing." +
                                     "\n(Make sure the chain ends in a datatype property)")

            properties.append(OwlRdyDatatypeProperty(_property))

            # Add property chain to the python parameter list
            param_list.append(DLPropertyChain(properties))

            # Get next item in param list
            params = params.tail[0] if params.tail else None

        return param_list

    def list_val_params(self, instance: OwlRdyInstance, params: list[DLPropertyChain]):
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

                # Build a list of results for the current property
                current_list = [x for instance in current_list for x in prop[instance]]

            # Add the final values to the list (end of property chain)
            list_values.append(current_list)
        res_list = it.product(*list_values)
        return res_list

    def calls_for_instance(self, instance: OwlRdyInstance) -> Generator[CallFormula, None, None]:
        # does not return a list but a generator
        return (call for call in self.calls if isinstance(instance.get(), call.get_domain().get()))

    def reason(self) -> bool:
        try:
            with self.onto:
                owl.sync_reasoner(infer_property_values=True, debug=False)
            return True
        except owl.OwlReadyInconsistentOntologyError:
            return False

    def add_object_prop_assertions(self, call: CallFormula, result: tuple[str, list[tuple]],
                                   instance: OwlRdyInstance, assertions: list[Assertion]) -> ValuesView[OwlRdyInstance]:

        inst, new_assertions = result
        # creates the (main) new instance
        main_instance = OwlRdyInstance(call.get_range().get()())
        assertions.append(ObjectPropertyAssertion(call.get_subsuming_property(), instance, main_instance))
        assertions.append(ClassAssertion(call.get_range(), main_instance))
        new_instances: dict[str, OwlRdyInstance] = {inst: main_instance}

        # there are 2 types of assertions
        # 2 elements means a class assertion and 3 elements a property assertion
        # we prioritize class assertions cause creating an instance with a concept is better
        # otherwise we'll get "Thing1" etc...
        new_assertions.sort(key=lambda x: len(x))
        for assertion in new_assertions:
            if len(assertion) == 2:
                concept, new_inst = assertion
                concept = getattr(self.namespace, concept)
                # concept not recognized
                if concept is None:
                    logging.warning(
                        f"The class {concept} was not found (From {self} function). Assertion '{assertion}' ignored.")
                    continue

                if new_inst in new_instances:
                    new_instances[new_inst].get().is_a.append(concept)
                else:
                    new_instances[new_inst] = OwlRdyInstance(concept())
                assertions.append(ClassAssertion(OwlRdyClass(concept), new_instances[new_inst]))

            elif len(assertion) == 3:
                inst1, prop, value = assertion
                prop = getattr(self.namespace, prop)
                if prop is None:
                    logging.warning(
                        f"The property {prop} was not found (From {self} function). Assertion '{assertion}' ignored.")
                    continue

                if inst1 not in new_instances:
                    new_instances[inst1] = OwlRdyInstance(owl.Thing(namespace=self.onto))

                if isinstance(prop, owl.ObjectPropertyClass):
                    if value not in new_instances:
                        new_instances[value] = OwlRdyInstance(owl.Thing(namespace=self.onto))
                    assertions.append(
                        ObjectPropertyAssertion(OwlRdyObjectProperty(prop), new_instances[inst1], new_instances[value]))
                else:
                    assertions.append(
                        DatatypePropertyAssertion(OwlRdyDatatypeProperty(prop), new_instances[inst1], value))

        return new_instances.values()
