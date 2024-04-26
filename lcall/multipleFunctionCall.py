from lcall.functionCall import FunctionCall
from lcall.datatypeFunctionCall import DatatypeFunctionCall
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from owlready2 import ThingClass, ClassConstruct, Namespace

class MultipleFunctionCall(FunctionCall):
    """
    A call can have multiple functions if it needs to fill multiple datatype properties.
    This is repfunctionsenting the FunctionCallList Class on call.rdf.

    It repfunctionsents a list of FunctionCall ('callableThing/Functions and Parameters' or 'FunctionCallList/MultipleFunctionCall')
    Each element of the list (head) has either one objectProperty annotation or one datatypeProperty annotation

    The annotations are useful to know which function fills which property.

    At the end, it is repfunctionsented by a dict.
    For example, let's say you have to create 
    a class A with the datatype properties hasX and hasZ 
    and the object property hasY which needs an instance of the class B with the data property hasT

    The functionsulting dict will be :

    { hasX : datatypeFunCallGetX ; hasY : { hasT : datatypeFunCallGetT } ; hasZ : datatypeFunCallGetZ }
    """

    def __init__(self, functionCall: (ThingClass | ClassConstruct), call: Namespace):
        """
        Initialization

        :param functionCall: the FuntionCallList instance containing the informations about the properties and functions to call
        :param call: the namespace (useful in DatatypeFunctionCall)
        """
        self.functions = {}
        self.params = None
        current = functionCall
        try:
            head = current.hasFunctionCallListHead
            while head:
                if head.hasObjectProperty:
                    function = MultipleFunctionCall(head, call)
                    if function:
                        self.functions[OwlRdyObjectProperty(head.hasObjectProperty[0])] = function.get_functions()
                    else:
                        return None
                elif head.hasDatatypeProperty:
                    function = DatatypeFunctionCall(head, call)
                    if function:
                        self.functions[OwlRdyDatatypeProperty(head.hasDatatypeProperty[0])] = function
                        self.params = function.get_parameters()
                    else:
                        return None
                else: # head property not specified
                    print("ERROR : '"+head.name+"' doesn't have any (annotation) property.")
                    return None
                current = current.hasFunctionCallListTail
                head = current.hasFunctionCallListHead if current else None
        # there was an error with one of the attributes, the program can't run properly
        except AttributeError as e:
            print("ERROR :", e)
            exit(-1)
    
    def exec(self, params):
        return self.rec_exec(self.functions, params)
    
    def rec_exec(self, props, params):
        results = {}
        for key, value in props.items():
            r = self.rec_exec(value, params) if isinstance(value, dict) else value.exec(params)
            if r is None:
                return None
            else:
                results[key] = r
        return results

    def get_functions(self):
        return self.functions
    
    def get_parameters(self) -> list[DLPropertyChain]:
        return self.params
    
    def __repr__(self) -> str:
        return str(self.functions)