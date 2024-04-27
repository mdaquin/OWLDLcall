from lcall.functionCall import FunctionCall
from lcall.pythonFunction import PythonFunction
from lcall.httpFunction import HTTPFunction
from lcall.DLPropertyChain import DLPropertyChain
from owlready2 import Thing, Namespace
import logging

def get_function(functionCall: Thing, call: Namespace):
    """
    Encapsulates the function

    :param functionCall: the call:CallableThing instance (basically the function)
    :param call: the ontology namespace to get the CallableThing classes
    """
    item_called_function = functionCall.functionToCall
    if isinstance(item_called_function, call.PythonFunction):
        call_expr = item_called_function.hasPyExpr
        call_exec = item_called_function.hasPyExec
        called_function = PythonFunction(call_expr, call_exec)
    elif isinstance(item_called_function, call.HTTPFunction):
        call_url = item_called_function.hasHttpURL
        call_auth = item_called_function.hasHttpAuth
        called_function = HTTPFunction(call_url, call_auth)
    else:
        logging.warning(str(item_called_function)+" is not recognized as a function.")
        return None
    return called_function

class DatatypeFunctionCall(FunctionCall):
    """
    Represents a function that returns a datatype
    """

    def __init__(self, functionCall: Thing, parameters: list[DLPropertyChain], call: Namespace):
        res = get_function(functionCall, call)
        if res:
            self.called_function = res
            self.parameters = parameters
        else:
            return None
    
    def exec(self, parameters):
        return self.called_function.exec(parameters)

    def get_parameters(self) -> list[DLPropertyChain]:
        return self.parameters
    
    def __repr__(self) -> str:
        return self.called_function.expr_code