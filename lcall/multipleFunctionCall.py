from lcall.functionCall import FunctionCall
from lcall.datatypeFunctionCall import DatatypeFunctionCall
from lcall.DLPropertyChain import DLPropertyChain

class MultipleFunctionCall(FunctionCall):
    def __init__(self, functionCall, call):
        self.res = {}
        self.params = None
        current = functionCall
        while True:
            head = current.hasFunctionCallListHead[0]
            if len(current.hasObjectProperty) > 0:
                function = MultipleFunctionCall(head, call)
                if function:
                    self.res[current.hasObjectProperty[0]] = function.res
                else:
                    return None
            elif len(head.hasDatatypeProperty) > 0:
                function = DatatypeFunctionCall(head, call)
                if function:
                    self.res[head.hasDatatypeProperty[0]] = function
                    self.params = function.get_parameters()
                else:
                    return None
            else:
                return None

            if len(current.hasFunctionCallListTail) == 0:
                break
            else:
                current = current.hasFunctionCallListTail[0]
    
    def exec(self, params):
        return self.executeOnDict(self.res, params)
    
    def executeOnDict(self, props, params):
        res_dict = {}
        for key, value in props.items():
            r = self.executeOnDict(value, params) if isinstance(value, dict) else value.exec(params)
            if r is None:
                return None
            else:
                res_dict[key] = r
        return res_dict

    def get_parameters(self) -> list[DLPropertyChain]:
        return self.params
    
    def __repr__(self) -> str:
        return str(self.res)