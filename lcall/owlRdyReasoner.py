import owlready2 as owl
import itertools as it
import logging

from lcall.DLPropertyChain import DLPropertyChain
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
        # if the CallFormula class doesn't exist
        if not call.CallFormula:
            logging.error("Class 'CallFormula' not found.")
            exit(-1)

        for item in call.CallFormula.instances():
            # message to show when there is a problem with a call and it has to be skipped
            skipCallMessage = "call '"+str(item)+"' ignored."

            # Get all call:CallFormula instances and creates python CallFormula instances from them

            # try cause those are added annotations
            try:
                item_subsumes = item.subsumingProperty
                item_function_calls = item.hasFunctionCall
                item_domain = item.domain
                item_range = item.range
            except AttributeError as e:
                # if one of the attribute is not defined (for example the ontology has been changed without considering the code)
                logging.error(e)
                exit(-1)

            # checks that the subsuming property is defined (required)
            if not item_subsumes:
                self.log_call_error("Subsuming property not defined for call '"+str(item)+"'", skipCallMessage)
                # we skip this call
                continue
            else:
                item_subsumes = item_subsumes[0]

            # check if the functionCall is defined (required)
            if not item_function_calls:
                self.log_call_error("functionCall not defined for call '"+str(item)+"'.\nIf you won't call any function (only possible with the subsuming property being an object property) create an empty FunctionCallList.",
                                    skipCallMessage)
                continue

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
            try:
                parameters = self.build_param_list(item_function_calls.hasParams)
                # we found a problem during the building of parameters
                if parameters is None:
                    logging.info(skipCallMessage)
                    continue
            
            # if "hasParams" isn't recognized
            except AttributeError as e:
                logging.error(e)
                exit(-1)

            # the subsuming property is an object property
            if isinstance(item_subsumes, owl.ObjectPropertyClass):

                # verify that the range is a class
                if not isinstance(item_range, owl.ThingClass):
                    self.log_call_error(f'Range ({item_range}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a class.',
                                        skipCallMessage)
                    continue

                # verify that the functionCall is an instance of FuntionCallList

                # if the class doesn't exist, there is a problem
                if not call.FunctionCallList:
                    logging.error("Class 'FunctionCallList' not found.")
                    exit(-1)

                if not isinstance(item_function_calls, call.FunctionCallList):
                    self.log_call_error(f'FunctionCall ({item_function_calls}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nThe functionCall should be an instance of {call.FunctionCallList}.',
                                        skipCallMessage)
                    continue
                
                item_range = OwlRdyClass(item_range)
                item_function_calls = MultipleFunctionCall(item_function_calls, parameters, call)
                item_subsumes = OwlRdyObjectProperty(item_subsumes)

            # the subsuming property is a datatype property
            elif isinstance(item_subsumes, owl.DataPropertyClass):

                # verify that the range is a datatype
                # None means the datatype has not been declared and we won't try to convert and just take the result of the function
                if item_range is not None and not isinstance(item_range, type):
                    self.log_call_error(f'Range ({item_range}) is not compatible with the (datatype) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a datatype.',
                                        skipCallMessage)
                    continue

                # verify that the functionCall is an instance of FuntionCallList
                if not call.DatatypeFunctionCall:
                    logging.error("Class 'DatatypeFunctionCall' not found.")
                    exit(-1)

                if not isinstance(item_function_calls, call.DatatypeFunctionCall):
                    self.log_call_error(f'FunctionCall ({item_function_calls}) is not compatible with the (datatype) subsuming property ({item_subsumes}) for call "{item}".\nThe functionCall should be an instance of {call.DatatypeFunctionCall}.',
                                        skipCallMessage)
                    continue
                
                item_range = OwlRdyDatatype(item_range)
                item_function_calls = DatatypeFunctionCall(item_function_calls, parameters, call)
                item_subsumes = OwlRdyDatatypeProperty(item_subsumes)
            else:
                # if the subsuming property is not a property
                self.log_call_error("Subsuming property is not a property.", skipCallMessage)
                continue
            
            # if there was an error during the encapsulation of the function (or functions)
            if not item_function_calls:
                logging.info(skipCallMessage)
                continue

            formula = CallFormula(item.name, item_subsumes, item_function_calls, OwlRdyClass(item_domain), item_range)
            self.calls.append(formula)
    
    # just log a error during the creation of a call
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
        res = []
        for ind in self.onto.individuals():
            res.append(OwlRdyInstance(ind))
        return res
    
    def build_param_list(self, params: owl.Thing) -> (list[DLPropertyChain] | None):
        """
        Build the list of parameters (property chains) from a call:ParamList instance

        :param params: call:ParamList instance of the parameters
        :return: list of parameters (property chains)
        """
        param_list = []
        try:
            while params:
                # Get property chain from parameter
                prop_chain = params.paramListHead

                # if we don't find a propchain
                if not prop_chain:
                    logging.warning(str(params)+" missing a propChain head.")
                    return None
                # Get datatype property of the chain

                # if there is no datatype on this propchain
                if not prop_chain.hasDatatypeProperty:
                    logging.warning(str(prop_chain)+" missing a datatype property.")
                    return None
                
                datatype_prop = OwlRdyDatatypeProperty(prop_chain.hasDatatypeProperty[0])

                # Build object property chain
                object_prop = []
                object_prop_chain = prop_chain.hasObjectPropertyList

                while object_prop_chain:
                    # if there is no object property list head
                    if not object_prop_chain.objectPropertyListHead:
                        logging.warning(str(object_prop_chain)+" missing an object property list head.")
                        return None
                    
                    object_prop.append(OwlRdyObjectProperty(object_prop_chain.objectPropertyListHead[0]))
                    object_prop_chain = object_prop_chain.hasObjectPropertyList

                # Add property chain to the python parameter list
                param_list.append(DLPropertyChain(datatype_prop, *object_prop))

                # Get next item in param list
                params = params.paramListTail
        # if any of the attributes doesn't exist (paramListHead etc...)
        except AttributeError as e:
            logging.error(e)
            exit(-1)

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
            if isinstance(instance.get(), call.get_domain().get()):
                call_list.append(call)
        return call_list

    def reason(self):
        with self.onto:
            owl.sync_reasoner(infer_property_values=True, debug=False)
