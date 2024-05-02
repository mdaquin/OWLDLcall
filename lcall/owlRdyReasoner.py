import owlready2 as owl
import itertools as it
import logging

from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyClass import OwlRdyClass
from lcall.abstractReasoner import AbstractReasoner
from lcall.callFormula import CallFormula
from lcall.functionList import FunctionList
from lcall.owlRdyDatatype import OwlRdyDatatype
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyInstance import OwlRdyInstance
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.pythonFunction import PythonFunction
from lcall.httpFunction import HTTPFunction

def get_function(function: owl.Thing, call: owl.Namespace):
    """
    Encapsulates the function

    :param functionCall: the call:CallableThing instance (basically the function)
    :param call: the ontology namespace to get the CallableThing classes
    """
    if isinstance(function, call.PythonFunction):
        call_expr = function.hasPyExpr
        call_exec = function.hasPyExec
        called_function = PythonFunction(call_expr, call_exec)
    elif isinstance(function, call.HTTPFunction):
        call_url =function.hasHttpURL
        call_auth = function.hasHttpAuth
        called_function = HTTPFunction(call_url, call_auth)
    else:
        raise ValueError(str(function)+" is not recognized as a function.")
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
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)

        self.calls = []

        call = owl.get_namespace("https://k.loria.fr/ontologies/call")

        try:
            for item in call.CallFormula.instances():
                # message to show when there is a problem with a call and it has to be skipped
                skipCallMessage = "call '"+str(item)+"' ignored."

                # Get all call:CallFormula instances and creates python CallFormula instances from them
                try:
                    item_subsumes = item.subsumingProperty
                    item_function = item.functionToCall
                    item_parameters = item.hasParams
                    item_domain = item.domain
                    item_range = item.range

                    # checks that the subsuming property is defined (required)
                    if not item_subsumes:
                        self.log_call_error("Subsuming property not defined for call '"+str(item)+"'", skipCallMessage)
                        # we skip this call
                        continue
                    else:
                        item_subsumes = item_subsumes[0]

                    # check if the domain is defined
                    if not item_domain:
                        # if the domain is not defined, we look for the domain of the subsuming property
                        # if it's still not defined, take Thing
                        if item_subsumes.domain:
                            item_domain = item_subsumes.domain[0]
                        else:
                            item_domain = owl.Thing
                        logging.info("Domain not defined for call '"+str(item)+"' default domain is "+str(item_domain))
                    else:
                        item_domain = item_domain[0]

                    # check if the range is defined
                    if not item_range:
                        if item_subsumes.range:
                            item_range = item_subsumes.range[0]
                        else:
                            item_range = owl.Thing if isinstance(item_subsumes, owl.ObjectPropertyClass) else None
                        logging.info("Range not defined for call '"+str(item)+"' default range is "+str(item_range))
                    else:
                        item_range = item_range[0]

                    # encapsulate in classes and check cohesion between the types
                    # for example, if the subsuming property is an object property, the range can't be a datatype

                    # encapsulate the parameters list (propertyChain)
                    item_parameters = self.build_param_list(item_parameters)

                    # the subsuming property is an object property
                    if isinstance(item_subsumes, owl.ObjectPropertyClass):

                        # verify that the range is a class
                        if not isinstance(item_range, owl.ThingClass):
                            self.log_call_error(f'Range ({item_range}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a class.',
                                                skipCallMessage)
                            continue

                        # verify that the functionCall is an instance of FuntionCallList
                        if item_function and not isinstance(item_function, call.FunctionList):
                            self.log_call_error(f'Function ({item_function}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nThe function should be an instance of {call.FunctionList} or None.',
                                                skipCallMessage)
                            continue
                        
                        item_range = OwlRdyClass(item_range)
                        item_function = FunctionList(item_function, get_function, call)
                        item_subsumes = OwlRdyObjectProperty(item_subsumes)

                    # the subsuming property is a datatype property
                    elif isinstance(item_subsumes, owl.DataPropertyClass):

                        # verify that the range is a datatype
                        # None means the datatype has not been declared and we won't try to convert and just take the result of the function
                        if item_range is not None and not isinstance(item_range, type):
                            self.log_call_error(f'Range ({item_range}) is not compatible with the (datatype) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a datatype.',
                                                skipCallMessage)
                            continue

                        item_range = OwlRdyDatatype(item_range)
                        item_function = get_function(item_function, call)
                        item_subsumes = OwlRdyDatatypeProperty(item_subsumes)
                    else:
                        # if the subsuming property is not a property
                        self.log_call_error("Subsuming property is not a property.", skipCallMessage)
                        continue

                    formula = CallFormula(item.name, item_subsumes, item_function, item_parameters, OwlRdyClass(item_domain), item_range)
                    self.calls.append(formula)
                except ValueError as e:
                    self.log_call_error(str(e), skipCallMessage)
                    continue
        # if there is an unrecognized property name
        except AttributeError as e:
            logging.error(e)
            exit(-1)
    

    def log_call_error(self, message: str, skipMessage: str):
        """
        Log an error found during the creation of a call

        :param message: the error message
        :param skipMessage: the message indicating that the call is ignored
        """
        logging.warning(message)
        logging.info(skipMessage)


    def instances(self) -> list[OwlRdyInstance]:
        """
        Get individuals of the ontology

        :return: individuals of the ontology
        """
        return [OwlRdyInstance(ind) for ind in self.onto.individuals()]
    

    def build_param_list(self, params: owl.Thing) -> (list[DLPropertyChain] | None):
        """
        Build the list of parameters (property chains) from a call:ParamList instance

        :param params: call:ParamList instance of the parameters
        :return: list of parameters (property chains)
        """
        param_list = []
        while params:
            # Get property chain from parameter
            prop_chain = params.paramListHead

            # if we don't find a propchain
            if not prop_chain:
                raise ValueError(str(params)+" missing a propChain head.")

            # if there is no datatype on this propchain
            if not prop_chain.hasDatatypeProperty:
                raise ValueError(str(prop_chain)+" missing a datatype property.")
            
            # Build object property chain
            properties = [OwlRdyDatatypeProperty(prop_chain.hasDatatypeProperty[0])]
            object_prop_chain = prop_chain.hasObjectPropertyList

            while object_prop_chain:
                # if there is no object property list head
                if not object_prop_chain.objectPropertyListHead:
                    raise ValueError(str(object_prop_chain)+" missing an object property list head.")
                
                properties.append(OwlRdyObjectProperty(object_prop_chain.objectPropertyListHead[0]))
                object_prop_chain = object_prop_chain.objectPropertyListTail
            
            # Get datatype property of the chain

            # Add property chain to the python parameter list
            param_list.append(DLPropertyChain(properties))

            # Get next item in param list
            params = params.paramListTail

        return param_list


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

                # Build a list of results for the current property
                current_list = [x for instance in current_list for x in prop[instance]]
            # Add the final values to the list (end of property chain)
            list_values.append(current_list)
        res_list = it.product(*list_values)
        return res_list

    def calls_for_instance(self, instance: OwlRdyInstance):
        
        return (call for call in self.calls if isinstance(instance.get(), call.get_domain().get()))

    def reason(self):
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)
