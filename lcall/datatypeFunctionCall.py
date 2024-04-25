from lcall.functionCall import *

class DatatypeFunctionCall(FunctionCall):
    def __init__(self, functionCall, call):
        res = getFonctionAndParams(functionCall, call)
        if res:
            self.called_function, self.params = res
        else:
            return None
    
    def exec(self, params):
        return self.called_function.exec(params)
    
    def get_parameters(self) -> list[DLPropertyChain]:
        return self.params
    
    def __repr__(self) -> str:
        return str(self.called_function)