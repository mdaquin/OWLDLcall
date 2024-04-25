from lcall.functionCall import FunctionCall
from lcall.datatypeFunctionCall import DatatypeFunctionCall
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty

class MultipleFunctionCall(FunctionCall):
    def __init__(self, functionCall, call):
        self.res = {}
        self.params = None
        current = functionCall
        while current:
            head = current.hasFunctionCallListHead
            if len(head.hasObjectProperty) > 0:
                function = MultipleFunctionCall(head, call)
                if function:
                    self.res[OwlRdyObjectProperty(head.hasObjectProperty[0])] = function.res
                else:
                    return None
            elif len(head.hasDatatypeProperty) > 0:
                function = DatatypeFunctionCall(head, call)
                if function:
                    self.res[OwlRdyDatatypeProperty(head.hasDatatypeProperty[0])] = function
                    self.params = function.get_parameters()
                else:
                    return None
            else: # head property not specified
                return None
            current = current.hasFunctionCallListTail
    
    def exec(self, params):
        return self.rec_exec(self.res, params)
    
    def rec_exec(self, props, params):
        res_dict = {}
        for key, value in props.items():
            r = self.rec_exec(value, params) if isinstance(value, dict) else value.exec(params)
            if r is None:
                return None
            else:
                res_dict[key] = r
        return res_dict

    def get_parameters(self) -> list[DLPropertyChain]:
        return self.params
    
    def __repr__(self) -> str:
        return str(self.res)