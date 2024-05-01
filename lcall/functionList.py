from lcall.callableThing import CallableThing
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from owlready2 import Thing
from lcall.DLProperty import DLProperty
import logging

class FunctionList(CallableThing):
    """
    A call can have multiple functions if it needs to fill multiple datatype properties.
    This is the equivalent of the FunctionList Class on call.rdf.

    It represents a list of Functions (callableThing)
    Each element of the list (head) has either one objectProperty annotation or one datatypeProperty annotation

    The annotations are useful to know which function fills which property.

    At the end, it is represented by a list of triples.
    For example, let's say you have to create 
    a class A with the datatype properties hasX and hasZ 
    and the object property hasY which needs an instance of the class B with the data property hasT

    The resulting list will be :

    [(hasX, True, datatypeFunCallGetX) ; (hasY, False, [(hasT, True, datatypeFunCallGetT)]) ; (hasZ, True, datatypeFunCallGetZ)]

    The boolean means that it is a datatype, so if the function returns a list, 
    we can differentiate it from a set due to an object property
    """

    def __init__(self, function: Thing, get_function, call):
        """
        Initialization

        :param function:
        :param get_function: 
        :param call: the namespace
        """
        self.functions = []
        try:
            while function:
                head = function.functionListHead
                if function.hasObjectProperty:
                    self.functions.append((OwlRdyObjectProperty(function.hasObjectProperty[0]), 
                                           False, FunctionList(head, get_function, call)))
                elif function.hasDatatypeProperty:
                    self.functions.append((OwlRdyDatatypeProperty(function.hasDatatypeProperty[0]), 
                                           True, get_function(head, call)))
                else: # head not specified
                    raise ValueError(str(function)+" doesn't have any (annotation) property.")
                function = function.functionListTail

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