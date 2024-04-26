import owlready2 as owl
import itertools as it

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
            print("ERROR : Class 'CallFormula' not found.")
            exit(-1)
    
        for item in call.CallFormula.instances():
            goodCall = True
            # Get all call:CallFormula instances and creates python CallFormula instances from them

            # try cause those are added annotations
            try:
                item_subsumes = item.subsumingProperty
                item_function_calls = item.hasFunctionCall
                item_domain = item.domain
                item_range = item.range
            except AttributeError as e:
                # if one of the attribute is not defined (for example the ontology has been changed without considering the code)
                print("ERROR :", e)
                exit(-1)

            # checks that the subsuming property is defined (required)
            if not item_subsumes:
                print("ERROR : Subsuming property not defined for call '"+str(item)+"'")
                goodCall = False
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
                print("WARNING : Domain not defined for call '"+str(item)+"' default domain is "+str(item_domain))
            else:
                item_domain = item_domain[0]

            # check if the range is defined
            if not item_range:
                if item_subsumes.range:
                    item_range = item_subsumes.range[0]
                else:
                    item_range = owl.Thing if isinstance(item_subsumes, owl.ObjectPropertyClass) else None
                print("WARNING : Range not defined for call '"+str(item)+"' default range is "+str(item_range))
            else:
                item_range = item_range[0]

            # check if the functionCall is defined (required)
            if not item_function_calls:
                print("ERROR : functionCall not defined for call '"+str(item)+"'.\nIf you won't call any function (only possible with the subsuming property being an object property) create a FunctionCallList with no head, nor tail.")
                exit(-1)

            # encapsulate in classes and check cohesion between the types
            # for example, if the subsuming property is an object property, the range can't be a datatype

            # the subsuming property is an object property
            if isinstance(item_subsumes, owl.ObjectPropertyClass):

                # verify that the range is a class
                if not isinstance(item_range, owl.ThingClass):
                    print(f'ERROR : range ({item_range}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a class.')
                    goodCall = False

                # verify that the functionCall is an instance of FuntionCallList

                # if the class doesn't exist, there is a problem
                if not call.FunctionCallList:
                    print("ERROR : Class 'FunctionCallList' not found.")
                    exit(-1)

                if not isinstance(item_function_calls, call.FunctionCallList):
                    print(f'ERROR : functionCall ({item_function_calls}) is not compatible with the (object) subsuming property ({item_subsumes}) for call "{item}".\nThe functionCall should be an instance of {call.FunctionCallList}')
                    goodCall = False
                
                item_range = OwlRdyClass(item_range)
                item_function_calls = MultipleFunctionCall(item_function_calls, call)
                item_subsumes = OwlRdyObjectProperty(item_subsumes)

            # the subsuming property is a datatype property
            elif isinstance(item_subsumes, owl.DataPropertyClass):

                # verify that the range is a datatype
                # None means the datatype has not been declared and we won't try to convert and just take the result of the function
                if item_range is not None and not isinstance(item_range, type):
                    print(f'ERROR : range ({item_range}) is not compatible with the (datatype) subsuming property ({item_subsumes}) for call "{item}".\nRange should be a datatype.')
                    goodCall = False

                # verify that the functionCall is an instance of FuntionCallList
                if not call.DatatypeFunctionCall:
                    print("ERROR : Class 'DatatypeFunctionCall' not found.")
                    exit(-1)

                if not isinstance(item_function_calls, call.DatatypeFunctionCall):
                    print(f'ERROR : functionCall ({item_function_calls}) is not compatible with the (datatype) subsuming property ({item_subsumes}) for call "{item}".\nThe functionCall should be an instance of {call.DatatypeFunctionCall}')
                    goodCall = False
                
                item_range = OwlRdyDatatype(item_range)
                item_function_calls = DatatypeFunctionCall(item_function_calls, call)
                item_subsumes = OwlRdyDatatypeProperty(item_subsumes)
            else:
                print("ERROR : subsuming property is not a property.")
                goodCall = False
            
            if not goodCall or not item_function_calls:
                print("INFO : call '"+item.name+"' ignored.")
            else:
                formula = CallFormula(item.name, item_subsumes, item_function_calls, OwlRdyClass(item_domain), item_range)
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
