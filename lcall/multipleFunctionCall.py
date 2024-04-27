from lcall.functionCall import FunctionCall
from lcall.datatypeFunctionCall import DatatypeFunctionCall
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from owlready2 import ThingClass, ClassConstruct, Namespace
from lcall.DLProperty import DLProperty
import logging

class MultipleFunctionCall(FunctionCall):
    """
    A call can have multiple functions if it needs to fill multiple datatype properties.
    This is equivalent to the FunctionCallList Class on call.rdf.

    It represents a list of FunctionCall ('callableThing/Functions and Parameters' or 'FunctionCallList/MultipleFunctionCall')
    and it has a parameters list (the hasParams property)
    Each element of the list (head) has either one objectProperty annotation or one datatypeProperty annotation

    The annotations are useful to know which function fills which property.

    At the end, it is represented by a list of triples.
    For example, let's say you have to create 
    a class A with the datatype properties hasX and hasZ 
    and the object property hasY which needs an instance of the class B with the data property hasT

    The resulting list will be :

    [(hasX, True, datatypeFunCallGetX) ; (hasY, False, [(hasT, True, datatypeFunCallGetT)]) ; (hasZ, True, datatypeFunCallGetZ)]
    The boolean means that it is a datatype, so if the function returns a set, we can differentiate it from a set due to an object property
    """

    def __init__(self, functionCall: (ThingClass | ClassConstruct), parameters: list[DLPropertyChain], call: Namespace):
        """
        Initialization

        :param functionCall: the FuntionCallList instance containing the informations about the properties and functions to call
        :param parameters: the list of parameters of the functions (every function shares the same list of parameters)
        :param call: the namespace (for hardcoded classes in the getFunction function in datatypeFunctionCall)
        """
        self.functions = []
        self.parameters = parameters
        current = functionCall
        try:
            # head of the list (can be None)
            head = current.functionCallListHead
            while head:
                if head.hasObjectProperty:
                    function = MultipleFunctionCall(head, parameters, call)
                    if function:
                        self.functions.append((OwlRdyObjectProperty(head.hasObjectProperty[0]), False, function))
                    else:
                        return None
                elif head.hasDatatypeProperty:
                    function = DatatypeFunctionCall(head, parameters, call)
                    if function:
                        self.functions.append((OwlRdyDatatypeProperty(head.hasDatatypeProperty[0]), True, function))
                    else:
                        return None
                else: # head property not specified
                    logging.warning(str(head)+" doesn't have any (annotation) property.")
                    return None
                current = current.functionCallListTail
                head = current.functionCallListHead if current else None
        # there was an error with one of the attributes, the program can't run properly
        except AttributeError as e:
            logging.error(e)
            exit(-1)
    

    def exec(self, parameters):
        result = []
        for property, isDatatype, value in self.functions:
            res = value.exec(parameters)
            if res:
                result.append((property, isDatatype, res))
            else:
                return None # failure
        return result

    def get_functions(self) -> list[DLProperty]:
        return self.functions
    
    def get_parameters(self) -> list[DLPropertyChain]:
        return self.parameters
    
    def __repr__(self) -> str:
        return str(self.functions)