from lcall.callableThing import CallableThing
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from owlready2 import Thing, Namespace
from lcall.DLProperty import DLProperty
from lcall.owlRdyClass import OwlRdyClass
from lcall.owlRdyDatatype import OwlRdyDatatype
import logging
from typing import Any

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

    def __init__(self, function: Thing, get_function, call: Namespace):
        """
        Initialization

        :param function: 
        :param get_function: the function creating the right ('terminal') callableThing
        :param call: the namespace
        """
        self.functions = []
        while function:
            head = function.functionListHead
            if function.hasObjectProperty:
                if function.range:
                    range = function.range[0]
                elif function.hasObjectProperty[0].range:
                    range = function.hasObjectProperty[0].range[0]
                    logging.info("(annotation) range not specified for "+str(function)+". Range set to "+str(range))
                else:
                    range = None
                    logging.info("(annotation) range not specified for "+str(function)+". Range set to Thing.")
                self.functions.append((OwlRdyObjectProperty(function.hasObjectProperty[0]), 
                                        OwlRdyClass(range), FunctionList(head, get_function, call)))
            elif function.hasDatatypeProperty:
                if function.range:
                    range = function.range[0]
                elif function.hasDatatypeProperty[0].range:
                    range = function.hasDatatypeProperty[0].range[0]
                    logging.info("(annotation) range not specified for "+str(function)+". Range set to "+str(range))
                else:
                    range = None
                    logging.info("No range specified for "+str(function)+". No conversion will be made.")
                self.functions.append((OwlRdyDatatypeProperty(function.hasDatatypeProperty[0]), 
                                        OwlRdyDatatype(range), get_function(head, call)))
            else:
                raise ValueError(str(function)+" doesn't have any (annotation) property.")
            function = function.functionListTail

    def exec(self, parameters: list[Any]) -> (list[tuple[DLProperty, (OwlRdyClass | OwlRdyDatatype), Any]] | None):
        result = []
        for property, range, value in self.functions:
            res = value.exec(parameters)
            if res:
                result.append((property, range, res))
            else:
                return None # failure
        return result

    def get_functions(self) -> list[DLProperty]:
        return self.functions
    
    def get_parameters(self) -> list[DLPropertyChain]:
        return self.parameters
    
    def __repr__(self) -> str:
        return str(self.functions)