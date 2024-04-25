from abc import ABC, abstractmethod
from lcall.pythonFunction import PythonFunction
from lcall.httpFunction import HTTPFunction
from lcall.DLPropertyChain import DLPropertyChain
from lcall.owlRdyDatatypeProperty import OwlRdyDatatypeProperty
from lcall.owlRdyObjectProperty import OwlRdyObjectProperty
import owlready2 as owl

def build_param_list(params: owl.Thing) -> list[DLPropertyChain]:
    """
    Build the list of parameters (property chains) from a call:ParamList instance

    :param params: call:ParamList instance of the parameters
    :return: list of parameters (property chains)
    """
    call = owl.get_namespace("https://k.loria.fr/ontologies/call")
    param_list = []
    while params is not None:
        # Get property chain from parameter
        prop_chain = call.paramListHead[params][0]
        # Get datatype property of the chain
        datatype_prop = OwlRdyDatatypeProperty(call.hasDatatypeProperty[prop_chain][0])

        # Build object property chain
        object_prop = []
        object_prop_chain_onto = call.hasObjectPropertyList[prop_chain]
        object_prop_chain = object_prop_chain_onto[0] if len(object_prop_chain_onto) != 0 else None

        while object_prop_chain is not None:
            object_prop.append(OwlRdyObjectProperty(call.objectPropertyListHead[object_prop_chain][0]))
            object_prop_chain_onto = call.hasObjectPropertyList[object_prop_chain]
            object_prop_chain = object_prop_chain_onto[0] if len(object_prop_chain_onto) != 0 else None

        # Add property chain to the python parameter list
        param_list.append(DLPropertyChain(datatype_prop, *object_prop))

        # Get next item in param list
        params_onto = call.paramListTail[params]
        params = params_onto[0] if len(params_onto) != 0 else None

    return param_list

def getFonctionAndParams(functionCall, call):
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
        return None
    return called_function, build_param_list(functionCall.hasParams)

class FunctionCall(ABC):

    @abstractmethod
    def get_parameters(self) -> list[DLPropertyChain]:
        pass